import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# ---------------------------------------------------------------- 1. story
layers = [('Apps: browser, Zoom, VS Code', 'card'), ('Shell / desktop', 'acc'), ('Kernel', 'blue'), ('Hardware: CPU · RAM · disk · Wi-Fi', 'green')]
sc = ''.join(box(26, 18 + k * 30, 230, 24, tone) + t(141, 34 + k * 30, name, 8.8, bold=(k == 2)) for k, (name, tone) in enumerate(layers))
sc += (t(290, 30, 'Riya’s laptop: Windows', 8.6, 'ink2', anchor='start') + t(290, 46, 'Kabir’s phone: Android', 8.6, 'ink2', anchor='start')
       + t(290, 62, 'The office server: Ubuntu', 8.6, 'ink2', anchor='start') + t(290, 88, 'Different looks, same four layers.', 9, 'acc', anchor='start', bold=True)
       + t(290, 104, 'Android and Ubuntu even share the', 8.6, 'ink2', anchor='start') + t(290, 118, 'same kernel: Linux.', 8.6, 'blue', anchor='start', bold=True))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Is Linux like Windows?”</h2>
  <div class="story">
''' + puzzle('When you type <code>ls</code>, two programs are involved: the shell (bash) and ls. Neither of them is allowed to touch the disk. So who reads the folder from the disk, and how could you <i>prove</i> it with one command?') + '''
    <p class="narration">Lunch break at the office. Riya has her Windows laptop open, Kabir is scrolling on his Android phone, and the office servers run Ubuntu. Riya asks the question every beginner asks: “Is Linux just another Windows?” Kabir laughs and says, “Your phone is already running Linux.” Riya is not convinced.</p>
''' + scene('Four layers of every computer: apps, shell or desktop, kernel and hardware, with a note that a Windows laptop, an Android phone and an Ubuntu server all have them.', sc,
            'Every device has the same layers. <tspan font-weight="700" class="s-acc">Linux is the kernel layer.</tspan>') + '''
R> Kabir, that cannot be true. My phone has no terminal, no black screen. How is it Linux?
A> Kabir is right, and your doubt is a good one. The word “Linux” is used for two things. Strictly, <b>Linux is a kernel</b>: the core program that controls the hardware. Android uses that kernel. Ubuntu uses the same kernel with a different set of programs on top.
K> So the kernel is the engine, and Android and Ubuntu are two different cars built on it?
A> A good picture. And Windows is a different car with a different engine. Today we will open the bonnet: what an <b>operating system</b> is, what the <b>kernel</b> and the <b>shell</b> do, and the 50-year story of how a lab project called Unix led a Finnish student to write Linux.
R> And why should I, as a future data engineer, care about engines?
A> Because every “permission denied”, every “out of memory”, every slow server you will ever debug is the kernel telling you something. Knowing who does what saves hours.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
lv = levels4('The operating system at four depths', [
    ('v', 'No jargon: an onion of layers', '''      <p>Think of every computer, phone or server as an onion. You only ever touch the outer skin. Every request you make travels inwards, and the answer comes back out.</p>''' + '''<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="An onion of layers: hardware in the centre, the kernel around it, the shell around that, and apps on the outside. You touch only the outer layer.">''' + '<circle cx="170" cy="110" r="100" class="s-card2" style="stroke:var(--line)"/><circle cx="170" cy="110" r="76" class="s-soft-acc" style="stroke:var(--track)"/><circle cx="170" cy="110" r="52" class="s-soft-blue" style="stroke:var(--blue)"/><circle cx="170" cy="110" r="28" class="s-soft-green" style="stroke:var(--green)"/>' + t(170, 114, 'Hardware', 8.6, 'green', bold=True) + t(170, 74, 'Kernel', 9, 'blue', bold=True) + t(170, 46, 'Shell', 9, 'acc', bold=True) + t(170, 22, 'Apps', 9, 'ink2', bold=True) + t(300, 40, 'You only ever touch the outside: apps and the shell.', 9.4, anchor='start', bold=True) + t(300, 64, 'Every request travels inwards, layer by layer:', 9, 'ink2', anchor='start') + t(300, 86, 'you → shell → kernel → hardware', 9.4, 'acc', anchor='start', mono=True, bold=True) + t(300, 110, 'The answer travels back outwards the same way.', 9, 'ink2', anchor='start') + t(300, 140, 'Only the kernel touches the hardware.', 9.4, 'blue', anchor='start', bold=True) + t(300, 162, 'That rule keeps programs from damaging each', 9, 'ink2', anchor='start') + t(300, 178, 'other or the machine.', 9, 'ink2', anchor='start') + '''<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>''' + '''
      <ul>
        <li><b>Hardware</b> (centre): the physical machine.</li>
        <li><b>Kernel</b>: the one program allowed to control the hardware.</li>
        <li><b>Shell</b>: the program that takes your typed request to the kernel.</li>
        <li><b>Apps</b>: browsers, games, Excel, the commands you run.</li>
        <li>All of it together is the <b>operating system</b> plus your apps.</li>
      </ul>'''),
    ('b', 'A restaurant', '''      <ul>
        <li><b>Hardware</b> is the kitchen equipment: stove, fridge, store room.</li>
        <li>The <b>kernel</b> is the head chef who alone controls the kitchen. No customer walks into the kitchen; every order goes through the chef, who decides what is cooked when and keeps orders from mixing up.</li>
        <li>The <b>shell</b> is the waiter: you tell it what you want, it carries the order in and brings the result back.</li>
        <li><b>Programs</b> (apps, commands) are the dishes on the menu. The operating system is the whole restaurant working together.</li>
      </ul>'''),
    ('i', 'The kernel’s five jobs, and where the shell fits', '''      <ul>
        <li><b>Process management:</b> starts and stops programs and shares the CPU between them many times a second (scheduling).</li>
        <li><b>Memory management:</b> gives each program its own private memory and stops one program from reading another’s.</li>
        <li><b>File systems:</b> turns names like <code>/home/riya/notes.txt</code> into blocks on a disk, and checks permissions.</li>
        <li><b>Devices:</b> drivers for disks, keyboards, network cards, USB, GPUs.</li>
        <li><b>Networking and security:</b> TCP/IP, firewall rules, users and permissions.</li>
        <li>The <b>shell</b> (usually <code>bash</code>) is <b>not</b> part of the kernel. It is an ordinary program that reads your commands and asks the kernel to run them. You can switch shells (bash, zsh, fish) without changing the kernel.</li>
      </ul>'''),
    ('a', 'User space, kernel space and system calls', '''      <ul>
        <li>The CPU has privilege levels. The kernel runs in <b>kernel space</b> with full access to hardware; every program, including the shell and even programs run by root, runs in <b>user space</b>.</li>
        <li>A program asks the kernel for anything (open a file, allocate memory, start a process, send a packet) through a <b>system call</b>: <code>openat</code>, <code>read</code>, <code>write</code>, <code>fork</code>/<code>clone</code>, <code>execve</code>, <code>socket</code>. A few hundred exist.</li>
        <li>Linux is a <b>monolithic</b> kernel: drivers and file systems run inside the kernel for speed, but they can be loaded at run time as <b>modules</b> (<code>lsmod</code>, <code>modprobe</code>).</li>
        <li>You can watch system calls live with <code>strace</code> and read kernel data in the virtual folder <code>/proc</code>. The “Run on your PC” panel below shows both.</li>
        <li><b>Protection rings:</b> on x86 the kernel runs in ring 0 and programs in ring 3 (ARM calls them exception levels EL1 and EL0). A system call is the controlled jump from ring 3 to ring 0 and back.</li>
        <li><b>Interrupts:</b> hardware (a key press, a network packet, a disk finishing a read, the timer) interrupts the CPU; the kernel runs a short handler in <b>interrupt context</b>, then usually wakes a waiting process. Code running for a process (for example inside a system call) runs in <b>process context</b>. See <code>/proc/interrupts</code>.</li>
        <li><b>One address space, two halves:</b> the kernel is mapped into the top of every process’s virtual address space, protected so that user mode cannot touch it; that makes system calls fast.</li>
        <li><b>Preemption and SMP:</b> Linux is a preemptive multitasking kernel: the scheduler can take the CPU away from a task at any time. It is also SMP: the kernel runs on all cores at once, which is why it uses locks such as spinlocks internally.</li>
      </ul>'''),
])

definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Operating system, kernel and shell</h2>
''' + def_block(
    'An <b>operating system (OS)</b> is the system software that manages a computer’s hardware and provides common services to programs. Its core is the <b>kernel</b>, which runs with full hardware privileges and is responsible for process scheduling, memory management, file systems, device drivers, networking and security; programs request these services through <b>system calls</b>. A <b>shell</b> is a user-space program that provides an interface to the operating system, reading commands from a user or a script and executing them.',
    'The kernel is the boss of the hardware; everything else must ask it. The shell is the program that takes your typed commands to the kernel. The operating system is the kernel plus all the basic programs around it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Kernel', f'The core of the OS. Controls CPU, memory, disks and devices. {gl("kernel", "Glossary →")}'),
    ('Shell', f'A program that reads commands and runs them. bash is the usual one. {gl("shell", "Glossary →")}'),
    ('System call', f'A request from a program to the kernel: open, read, write, execve. {gl("system-call", "Glossary →")}'),
    ('User space / kernel space', f'Where normal programs run vs where the kernel runs. {gl("user-space-vs-kernel-space", "Glossary →")}'),
    ('Process', f'A program that is running right now. {gl("process", "Glossary →")}'),
    ('Unix', f'The 1969 Bell Labs operating system whose ideas Linux follows. {gl("unix", "Glossary →")}'),
    ('GNU', f'Free tools (bash, ls, gcc) that complete the Linux kernel into an OS. {gl("gnu", "Glossary →")}'),
    ('POSIX', 'A standard describing how Unix-like systems behave, so scripts and programs work across them.'),
    ('Kernel module', f'A piece of the kernel (often a driver) loaded while running. {gl("kernel-module", "Glossary →")}'),
    ('Distribution', f'Kernel + tools + package manager, ready to install: Ubuntu, RHEL. {gl("distribution-distro", "Glossary →")}'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Unix created', '1969 at Bell Labs, by Ken Thompson and Dennis Ritchie'),
    ('Unix rewritten in C', '1973, which made it portable to other computers'),
    ('GNU project started', '1983, by Richard Stallman, to build a free Unix-like system'),
    ('Linux announced', '25 August 1991, by Linus Torvalds, a student at the University of Helsinki'),
    ('Linux licence', 'GNU General Public License, version 2'),
    ('Kernel type', 'Monolithic, with loadable modules'),
    ('Default shell on most distros', 'bash (Ubuntu’s <code>/bin/sh</code> is dash, used for scripts)'),
]) + '\n' + names('The names in this lesson are short forms, jokes and accidents of history. Knowing them makes them stick.', [
    ('uname', 'Unix name', 'Prints the name (and version) of the system’s kernel.'),
    ('nproc', 'number of processing units', 'How many CPU cores you may use.'),
    ('strace', 'system-call trace', 'Traces every request a program makes to the kernel.'),
    ('lsmod', 'list modules', 'Lists the kernel modules (drivers) loaded right now.'),
    ('dmesg', 'display messages', 'Shows the kernel’s own message log.'),
    ('/proc', 'processes', 'A folder of live process and kernel information.'),
    ('bash', 'Bourne-again shell', 'A pun: it replaced the Bourne shell (sh) by Stephen Bourne.'),
    ('GNU', 'GNU’s Not Unix', 'A recursive joke: the G stands for GNU itself.'),
    ('Linux', 'Linus + Unix', 'Linus wanted “Freax”; the server admin who hosted it named the folder “linux”, and it stuck.'),
]) + '\n' + lv + didyou('The Linux kernel is one of the largest collaborative software projects ever: tens of millions of lines of code, with thousands of developers from hundreds of companies contributing to every release, and a new release roughly every nine to ten weeks.') + '''
EXAM> For “Explain the structure of an operating system” draw the four layers (hardware → kernel → shell/system programs → applications), list the kernel’s functions (process, memory, file, device, network/security management) and define system call. For Linux add: monolithic kernel with loadable modules, GPL v2.
''' + qc('Is bash part of the kernel?', 'No. bash is an ordinary user-space program (<code>/usr/bin/bash</code>). You can replace it with zsh or fish and the kernel does not change.') + '''
</section>
'''


# ---------------------------------------------------------------- kernel architecture (added after reviewing linux-kernel-labs, Scaler, zedas)
def _sub(x, y, w, name, src, tone):
    return label_box(x, y, w, 42, [name, src], tone, 8.6)
karch_svg = ('<div class="scene scene--wide"><svg viewBox="0 0 640 330" role="img" aria-label="Linux kernel architecture: applications and the C library in user space; the system call interface; kernel subsystems (process scheduler, memory management, virtual file system, block I/O, networking, IPC, security modules, device drivers); architecture-specific code; and hardware.">'
    + box(10, 8, 620, 52, 'card', rx=10) + t(24, 24, 'USER SPACE  (CPU ring 3 / unprivileged)', 8, 'ink3', anchor='start', bold=True)
    + ''.join(label_box(24 + k * 120, 30, 108, 24, [n], 'card', 8.4) for k, n in enumerate(['bash', 'ls, cat', 'nginx', 'python3', 'C library (glibc)']))
    + label_box(10, 68, 620, 26, ['System call interface: openat · read · write · clone · execve · mmap · socket …'], 'acc', 8.8)
    + box(10, 102, 620, 160, 'card', rx=10) + t(24, 118, 'KERNEL SPACE  (CPU ring 0 / privileged)', 8, 'ink3', anchor='start', bold=True)
    + _sub(24, 126, 142, 'Process scheduler', 'kernel/sched/', 'blue') + _sub(174, 126, 142, 'Memory management', 'mm/', 'blue')
    + _sub(324, 126, 142, 'Virtual file system', 'fs/', 'green') + _sub(474, 126, 142, 'Networking stack', 'net/', 'violet')
    + _sub(24, 174, 142, 'IPC: pipes, signals', 'ipc/, kernel/', 'blue') + _sub(174, 174, 142, 'Block I/O layer', 'block/', 'green')
    + _sub(324, 174, 142, 'Security modules', 'security/', 'red') + _sub(474, 174, 142, 'Device drivers', 'drivers/', 'amber')
    + label_box(24, 222, 592, 32, ['Architecture-specific code: boot, interrupts, page tables, context switch   (arch/x86, arch/arm64 …)'], 'card', 8.4)
    + label_box(10, 272, 620, 34, ['Hardware: CPU cores · RAM · SSD · network card · keyboard · GPU'], 'green', 9)
    + t(320, 322, 'Folders under each name are where that part lives in the Linux kernel source code.', 8.4, 'ink2')
    + '<text x="632" y="326" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')

kexplore = dissect('Inside the Linux kernel: explore its subsystems',
    'The diagram above is the classic map of the Linux kernel. Click each part to see what problem it solves, how it works, where its code lives in the kernel source tree, and a real window into it through <code>/proc</code> or <code>/sys</code> (recorded on our build machine).', [
    dict(key='sched', name='Process scheduler', sub='who runs next',
         why='Hundreds of tasks want a few CPU cores. Someone must decide, thousands of times a second, which one runs and for how long.',
         how='Each runnable task waits in a per-CPU queue; the scheduler picks the next one by fairness and priority (nice). Since Linux 6.6 the default algorithm is EEVDF, which replaced the older CFS. Each switch is a context switch.',
         impl='Source folder <code>kernel/sched/</code>. Counters in <code>/proc/stat</code>; tasks are <code>task_struct</code> objects inside the kernel.',
         used='Explains load average, CPU-hungry jobs and why <code>nice</code> matters (Modules 11 and 18).',
         cmd='grep ctxt /proc/stat'),
    dict(key='mm', name='Memory management', sub='who gets which RAM',
         why='Every program must believe it has its own private memory, and must not read or damage anyone else’s.',
         how='The kernel gives each process a virtual address space and maps it to real RAM in 4 KB pages using the CPU’s MMU. It uses spare RAM as a file cache, swaps rarely used pages to disk, and as a last resort runs the OOM killer.',
         impl='Source folder <code>mm/</code>; page tables are set up by architecture code. Numbers in <code>/proc/meminfo</code>.',
         used='Out-of-memory crashes, sizing servers, reading <code>free</code> correctly (Lesson 15.4).',
         cmd="grep -E '^(MemTotal|MemAvailable)' /proc/meminfo"),
    dict(key='vfs', name='Virtual file system (VFS)', sub='one interface for all disks',
         why='Disks use different formats (ext4, xfs, FAT, network shares). Programs should not care which.',
         how='Programs call open/read/write; the VFS translates them into calls to the right file-system driver, and keeps caches of names (dentries), inodes and file data (page cache).',
         impl='Source folder <code>fs/</code> (with <code>fs/ext4/</code>, <code>fs/xfs/</code> …). Supported file systems are listed in <code>/proc/filesystems</code>.',
         used='Mounting disks, USB sticks and network shares (Module 15); “everything is a file” (Lesson 2.1).',
         cmd='grep -v nodev /proc/filesystems'),
    dict(key='block', name='Block I/O layer', sub='queues disk requests',
         why='Disks are slow compared with the CPU. Requests should be merged and ordered so the disk works efficiently.',
         how='File-system requests become block requests; the layer merges neighbours, schedules them and hands them to the disk driver.',
         impl='Source folder <code>block/</code>. Per-disk statistics in <code>/proc/diskstats</code>; disks listed by <code>lsblk</code>.',
         used='Diagnosing slow disks with iostat (Lesson 18.3).',
         cmd='lsblk -d -o NAME,SIZE,TYPE | head -3'),
    dict(key='net', name='Networking stack', sub='TCP/IP inside the kernel',
         why='Every web request, SSH session and database connection needs reliable delivery of packets.',
         how='Programs use sockets; the kernel implements TCP, UDP and IP, routes packets, applies firewall rules (netfilter) and talks to network-card drivers.',
         impl='Source folder <code>net/</code>. Interface counters in <code>/proc/net/dev</code>.',
         used='Ports, firewalls, slow-network debugging (Modules 16 and 19).',
         cmd='head -3 /proc/net/dev'),
    dict(key='ipc', name='IPC', sub='processes talking to each other',
         why='Programs need to cooperate: pass data, send notifications, share memory.',
         how='The kernel provides pipes (<code>|</code>), signals (Ctrl+C), sockets, shared memory and message queues.',
         impl='Source folders <code>ipc/</code> and <code>kernel/</code> (signals); pipes live in <code>fs/pipe.c</code>.',
         used='Every pipeline you will write (Module 5), Ctrl+C and kill (Lesson 11.3).',
         cmd='kill -l | head -2'),
    dict(key='lsm', name='Security modules (LSM)', sub='extra rules on every access',
         why='Normal file permissions are not always enough; some systems need mandatory rules even for root.',
         how='The kernel calls security “hooks” before sensitive actions; modules such as SELinux or AppArmor answer allow or deny.',
         impl='Source folder <code>security/</code> (<code>security/selinux/</code>, <code>security/apparmor/</code>).',
         used='SELinux on RHEL, AppArmor on Ubuntu (Lesson 19.2).'),
    dict(key='drv', name='Device drivers', sub='talk to each piece of hardware',
         why='Thousands of different devices exist; each speaks its own language.',
         how='A driver translates generic kernel requests into commands for one kind of device. The kernel’s device model organises devices by bus (PCI, USB) and can load drivers as modules.',
         impl='Source folder <code>drivers/</code>, the biggest part of the kernel. Buses visible in <code>/sys/bus/</code>.',
         used='Why new hardware sometimes needs a newer kernel; <code>lsmod</code> and <code>lspci</code> (Lessons 18.5, 20.1).',
         cmd='ls /sys/bus | head -5'),
    dict(key='arch', name='Architecture code', sub='CPU-specific glue',
         why='Intel/AMD, ARM and RISC-V CPUs start, handle interrupts and manage page tables differently.',
         how='A thin layer per CPU family does boot set-up, interrupt entry, context switches and page-table handling, so everything above can stay generic.',
         impl='Source folder <code>arch/</code> (<code>arch/x86/</code>, <code>arch/arm64/</code>, <code>arch/riscv/</code>).',
         used='The reason one kernel runs on laptops, phones and Raspberry Pis.',
         cmd='uname -m'),
], hid='kernel-inside', hint='Click a subsystem of the kernel.')

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Kinds of kernels, kinds of shells</h2>
  <h3>Kernel designs</h3>
''' + table(['Design', 'Idea', 'Examples', 'Trade-off'], [
    ['Monolithic', 'Drivers, file systems and networking all run inside the kernel', '<b>Linux</b>, traditional Unix, FreeBSD', 'Fast; a buggy driver can crash the whole system'],
    ['Microkernel', 'Kernel does only the minimum; drivers run as separate programs', 'MINIX 3, QNX, seL4', 'Very robust; more messages, can be slower'],
    ['Hybrid', 'Microkernel structure with many parts moved back into the kernel', 'Windows NT family, macOS (XNU)', 'A middle path'],
], minw=640) + '''
  <p>Linux softens the monolithic trade-off with <b>loadable modules</b>: a Wi-Fi driver can be loaded when the card is detected and removed later, without rebooting.</p>

  <h3>Shells you will meet</h3>
''' + table(['Shell', 'Program', 'Where you will see it'], [
    ['Bourne shell', '<code>sh</code>', 'The original (1979). Today <code>/bin/sh</code> is a link to a compatible shell'],
    ['Bash', '<code>bash</code>', 'Default interactive shell on most Linux distros. This course uses it'],
    ['Dash', '<code>dash</code>', 'Ubuntu/Debian’s fast <code>/bin/sh</code> for system scripts'],
    ['Z shell', '<code>zsh</code>', 'Default on macOS since 2019; popular with developers'],
    ['Fish', '<code>fish</code>', 'Friendly shell with suggestions; not POSIX-compatible'],
    ['PowerShell', '<code>pwsh</code>', 'Windows’ shell; also runs on Linux'],
], minw=560) + '''
  <h3 id="kernel-map">Inside the Linux kernel: the architecture map</h3>
  <p>Linux is monolithic, but it is not a single blob. It is built from well-defined <b>subsystems</b>, each in its own folder of the source code. Programs reach all of them only through the system call interface.</p>
''' + karch_svg + kexplore + didyou('How a kernel release is made: after each release there is a two-week <b>merge window</b> in which Linus Torvalds pulls new features from subsystem maintainers (scheduler, networking, file systems…). Then come weekly release candidates (-rc1, -rc2…) with only fixes, and about nine to ten weeks later the next version is released.') + '''
  <h3>Who is “Linux”: the kernel or the OS?</h3>
''' + cards([
    ('Linux (strict meaning)', 'Only the kernel, maintained by Linus Torvalds and thousands of contributors at kernel.org.', 'kernel'),
    ('Linux (everyday meaning)', 'A full operating system using that kernel: Ubuntu, Fedora, Debian, RHEL.', 'distribution'),
    ('GNU/Linux', 'The name some people prefer, giving credit to the GNU tools that complete the system.', 'naming'),
    ('Android', 'Linux kernel + Google’s own user space (no GNU tools, no bash by default).', 'phones'),
]) + '''
''' + qc('A colleague’s Wi-Fi driver bug crashed the whole Linux laptop, not just one app. Which kernel design explains why that is possible?', 'Monolithic: drivers run inside the kernel, in kernel space, so a bad driver can take the whole kernel down. In a microkernel the driver would be a separate process.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps: history timeline
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From Unix to Linux in six steps</h2>
  <p>Linux makes much more sense once you know where its ideas came from. Each step says why it still matters to you.</p>
''' + stepper([
    ('1969 · Unix at Bell Labs', '<p>Bell Labs had left Multics, a large and ambitious operating system project. Ken Thompson and Dennis Ritchie wrote a much smaller system on a spare computer and called it Unix. Ideas: small tools that do one thing well, everything is a file, a shell to join tools together. Unix measures time in seconds since <b>1 January 1970</b>, the “Unix epoch”, still used by every Linux system today (<code>date +%s</code>).</p>',
     'Why it matters: pipes (<code>|</code>), files for everything and small commands are exactly what you will use in Modules 2–6.'),
    ('1973 · Rewritten in C', '<p>Unix is rewritten in the new C language, so it can be moved to other kinds of computers. Universities get the source code.</p>',
     'Why it matters: portability is why the same Linux runs on phones, laptops and supercomputers today.'),
    ('1970s–80s · Many Unixes', '<p>Universities create BSD; companies sell their own versions (Solaris, HP-UX, AIX). Unix is powerful but expensive and closed.</p>',
     'Why it matters: banks and telecoms still run some of these. The POSIX standard keeps them similar, so your skills carry over.'),
    ('1983 · The GNU project', '<p>Richard Stallman starts GNU to build a completely free Unix-like system and the GPL licence to keep it free. By 1991 GNU has a compiler, a shell (bash, 1989) and core tools, but no finished kernel.</p>',
     'Why it matters: <code>bash</code>, <code>ls</code>, <code>grep</code> and <code>gcc</code> on your Linux come from GNU.'),
    ('1991 · Linus writes a kernel', '<p>Linus Torvalds, a student in Helsinki who had been using Andrew Tanenbaum’s teaching system MINIX, announces a “hobby” kernel on 25 August 1991. Combined with the GNU tools, it becomes a complete free OS. In 1992 the kernel is released under the GPL, and version 1.0 arrives in March 1994.</p>',
     'Why it matters: thousands of volunteers and companies can improve the same kernel, which is why it grew so fast.'),
    ('Today · Linux everywhere', '<p>Distributions (Debian 1993, Red Hat 1994, Ubuntu 2004), Android (2008) and the cloud put the Linux kernel on billions of devices.</p>',
     'Why it matters: whatever IT role you take, from data engineering to DevOps, you will work on Linux machines.'),
]) + '''
''' + qc('Linux was written in 1991. Does it contain the original Unix code from Bell Labs?', 'No. Linux was written from scratch. It follows Unix’s design and the POSIX standard, which is why it is called Unix-like.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def lay(hl, notes=None):
    rows = [('Shell (bash)', 'acc', 'user space'), ('Program: ls', 'card', 'user space'), ('Kernel', 'blue', 'kernel space'), ('Disk + screen', 'green', 'hardware')]
    o = ''
    for k, (name, tone, sp) in enumerate(rows):
        on = k in hl
        o += box(14, 18 + k * 42, 140, 32, tone if on else 'card') + t(84, 38 + k * 42, name, 9, 'ink' if on else 'ink3', bold=on)
        o += t(162, 38 + k * 42, sp, 7.4, 'ink3', anchor='start')
    o += '<path d="M10 102H220" style="stroke:var(--ink-3);stroke-dasharray:4 3"/>'
    return o
see = [term(20, 22, 320, 130, ['$ ls'], ) + t(180, 178, 'Riya types ls (list files) and presses Enter.', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ ls']) + t(180, 178, '…', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ ls']) + t(180, 178, '…', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ ls']) + t(180, 178, '…', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ ls', 'notes.txt  report.csv  scripts']) + t(180, 178, 'The file names appear.', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ ls', 'notes.txt  report.csv  scripts', '$ '], cursor=True) + t(180, 178, 'Prompt back. Under 10 milliseconds in total.', 9, 'green', bold=True)]
def side(lines, cls='ink2'):
    return ''.join(t(290, 40 + k * 15, s, 8.2, cls if k else 'acc', bold=(k == 0)) for k, s in enumerate(lines))
behind = [lay([0]) + side(['bash reads “ls”', 'not a builtin, so it', 'searches PATH and finds', '/usr/bin/ls']),
          lay([0, 2]) + side(['system calls:', 'clone() → a child process', 'execve("/usr/bin/ls")', 'kernel loads ls into RAM']),
          lay([1, 2]) + side(['ls asks the kernel:', 'openat(".")', 'getdents64() →', '“give me the names”']),
          lay([1, 2, 3]) + side(['kernel reads the', 'directory from disk', '(or from its cache)', 'and copies names to ls']),
          lay([1, 2, 3]) + side(['ls sorts the names and', 'calls write(1, …)', 'kernel sends the bytes', 'to the terminal']),
          lay([0]) + side(['ls calls exit(0)', 'kernel frees its memory', 'bash was waiting (wait4)', 'and prints the prompt'])]
two = anim_two('ls', 'User space asks, kernel space does', 'A terminal running the ls command and printing three file names.',
               'Bash and ls in user space make system calls to the kernel, which reads the disk and writes to the screen.', see, behind,
               ['Riya types <code>ls</code> and presses Enter.', 'Nothing visible yet.', 'Still nothing visible: this all takes microseconds.', 'Still working behind the screen.', 'Three names appear.', 'The command is over and bash is ready again.'],
               ['bash looks at the first word. <code>ls</code> is not built into bash, so it searches the folders in <code>PATH</code> and finds the program file <code>/usr/bin/ls</code>.',
                'bash asks the kernel to create a child process (<code>clone</code>, the modern <code>fork</code>) and to run ls in it (<code>execve</code>). Only the kernel can start programs.',
                'ls cannot read the disk itself. It makes system calls: open the current directory, then <code>getdents64</code> = “get the directory entries”.',
                'The kernel’s file-system code reads the directory from disk, or from RAM if it was read recently (the page cache), and copies the names into ls’s memory.',
                'ls sorts the names and calls <code>write</code> on file descriptor 1 (its output). The kernel passes the bytes to the terminal, which draws them.',
                'ls exits. The kernel frees its memory and tells bash, which was waiting. You can see every one of these calls with <code>strace ls</code>.'])

# scenario 1: scheduling
def cpu(slots, label):
    cols = {'M': ('green', 'music'), 'B': ('blue', 'browser'), 'D': ('acc', 'download'), '-': ('grey', 'idle')}
    o = t(14, 30, label, 9, 'ink2', anchor='start')
    for k, c in enumerate(slots):
        o += fill(14 + k * 26, 40, 24, 30, cols[c][0], rx=3)
    o += ''.join(fill(14 + k * 92, 86, 12, 12, cols[c][0], rx=2) + t(30 + k * 92, 96, cols[c][1], 8, 'ink2', anchor='start') for k, c in enumerate('MBD'))
    return o
ca = cpu('MMMMMMMMMMMMM', 'Only music is playing: it gets every time slice') + cap('One CPU core, one program: easy.', '', 'card', y=130, h=34)
cb = cpu('MBMBMBMBMBMBM', 'Riya opens the browser') + cap('The kernel’s scheduler switches between them', 'every few milliseconds.', 'blue', y=130, h=46)
cc = cpu('MBDMBDMBDMBDM', 'A big download starts too') + cap('Three programs, one core: each gets turns.', 'Switching is so fast it feels simultaneous.', 'blue', y=130, h=46)
cd_ = cpu('MBMDMBMDMBMDM', 'Music must not stutter') + cap('The scheduler gives the music player its turn', 'often enough, so the audio never breaks.', 'green', y=130, h=46)
ce = (t(180, 30, 'Behind the scenes', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• This is process management: the kernel’s first job.', '• Real CPUs have several cores: the kernel spreads work', '   over them too.', '• You can watch it with top (Lesson 11.2).'])) + cap('Programs never fight for the CPU: the kernel decides.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Music, browser and a download on one CPU core',
              'Riya plays music while browsing and downloading. Each coloured block is a tiny time slice of one CPU core. Simplified, but this is really how the kernel shares a CPU.',
              'The kernel’s scheduler at work', 'Time slices on one CPU core being shared between a music player, a browser and a download.', [ca, cb, cc, cd_, ce],
              ['With one program, it can use every slice of CPU time.',
               'When the browser starts, the kernel alternates between the two, switching every few milliseconds.',
               'A download joins. Now three programs take turns on one core. To Riya, all three seem to run at once.',
               'The scheduler is fair but smart: the music player wakes up often enough that sound never stutters.',
               'Sharing the CPU is the kernel’s job. No program can grab the CPU forever, which is why one busy program does not freeze a well-run Linux machine.'],
              hid='scenario-scheduler')

# scenario 2: memory protection
def mem(states):
    o = ''
    for k, (name, st) in enumerate(states):
        tone = {'ok': 'green', 'bad': 'red', 'gone': 'card'}[st]
        o += label_box(14 + k * 114, 30, 104, 60, [name, {'ok': 'running', 'bad': 'crashed', 'gone': 'restarted'}[st]], tone, 9)
    return o
ma = mem([('Excel', 'ok'), ('Browser', 'ok'), ('Buggy app', 'ok')]) + cap('Three programs, each in its own private memory.', 'The kernel keeps walls between them.', 'card', y=120, h=46)
mb = mem([('Excel', 'ok'), ('Browser', 'ok'), ('Buggy app', 'ok')]) + arrow(290, 96, 190, 96, 'red', 2) + t(240, 110, 'tries to write here', 8, 'red') + cap('A bug makes one program write to memory', 'that is not its own.', 'red', y=120, h=46)
mc = mem([('Excel', 'ok'), ('Browser', 'ok'), ('Buggy app', 'bad')]) + t(294, 106, 'Segmentation fault', 8, 'red', bold=True, mono=True) + cap('The CPU traps it; the kernel stops only that program', '(“Segmentation fault”).', 'red', y=120, h=46)
md = mem([('Excel', 'ok'), ('Browser', 'ok'), ('Buggy app', 'gone')]) + cap('Excel and the browser never noticed.', 'The buggy app can simply be started again.', 'green', y=120, h=46)
me = (t(180, 30, 'Why servers love this', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• One bad program should not take down the server.', '• Memory protection = the kernel’s memory management.', '• A bug inside the kernel itself is different:', '   that causes a “kernel panic”.'])) + cap('Programs are isolated; the kernel is trusted.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'One program crashes, the others carry on',
              'Why does a crashing app not take down your whole computer? Because the kernel gives each process its own memory and enforces the walls.',
              'Memory protection', 'Three programs in separate memory; a buggy one tries to write outside its area and is stopped by the kernel while the others keep running.', [ma, mb, mc, md, me],
              ['Every process gets its own private memory. It cannot even see the others’ memory.',
               'A bug (for example a bad pointer in C) makes one program try to write somewhere it does not own.',
               'The CPU detects it and hands control to the kernel, which kills that one process. You see “Segmentation fault”.',
               'The other programs keep running untouched. Restart the buggy app and carry on.',
               'This isolation is why one bad service rarely brings down a Linux server. A bug in the kernel is different: it can stop everything (a kernel panic).'],
              hid='scenario-memory')

# scenario 3: one kernel, many systems
def dev(x, name, user, tone):
    return label_box(x, 18, 76, 40, [name, user], tone, 8) + arrow(x + 38, 60, x + 38, 84, 'ink3', 1.4)
ka = label_box(14, 86, 332, 30, ['Linux kernel (same code base)'], 'blue', 9.4) + cap('One kernel project at kernel.org.', '', 'card', y=150, h=34)
kb = ka[:0] + dev(14, 'Server', 'Ubuntu + GNU', 'green') + label_box(14, 86, 332, 30, ['Linux kernel (same code base)'], 'blue', 9.4) + cap('Servers: kernel + GNU tools + bash.', '', 'green', y=150, h=34)
kc = dev(14, 'Server', 'Ubuntu + GNU', 'green') + dev(98, 'Phone', 'Android', 'acc') + label_box(14, 86, 332, 30, ['Linux kernel (same code base)'], 'blue', 9.4) + cap('Phones: the same kernel + Android’s own user space.', '', 'acc', y=150, h=34)
kd = dev(14, 'Server', 'Ubuntu + GNU', 'green') + dev(98, 'Phone', 'Android', 'acc') + dev(182, 'Router', 'OpenWrt', 'violet') + dev(266, 'Super-', 'computer', 'amber') + label_box(14, 86, 332, 30, ['Linux kernel (same code base)'], 'blue', 9.4) + cap('Routers, TVs, cars, supercomputers: same kernel,', 'built with different options and drivers.', 'blue', y=150, h=44)
ke = (t(180, 30, 'What this means for you', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Kernel skills (processes, memory, files) apply everywhere.', '• The user space differs: commands on a server, apps on a phone.', '• Distributions are different user spaces on one kernel (Lesson 1.3).'])) + cap('Learn the layers once, use them on every device.', '', 'green', y=140, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One kernel, very different systems',
              'The same Linux kernel is compiled for servers, phones, routers and supercomputers. What changes is the user space on top and the drivers built in.',
              'One kernel, many user spaces', 'The Linux kernel at the bottom, with a server, a phone, a router and a supercomputer built on top of it.', [ka, kb, kc, kd, ke],
              ['The Linux kernel is one open-source project, developed at kernel.org by thousands of people.',
               'A server distribution such as Ubuntu adds the GNU tools, bash and a package manager.',
               'Android adds its own very different user space (apps, Java/Kotlin runtime). There is no bash in the user’s view, but the kernel is Linux.',
               'Routers, smart TVs and supercomputers build the kernel with the drivers they need and add a small or specialised user space.',
               'This is why “Linux” can mean a kernel or a whole system. In this course we work with server distributions, mostly Ubuntu and RHEL-family.'],
              hid='scenario-onekernel')


# scenario 4: an interrupt
def irq(hl, msg, extra=''):
    o = label_box(10, 14, 90, 36, ['Keyboard'], 'amber' if 0 in hl else 'card', 8.8)
    o += label_box(130, 14, 100, 36, ['CPU core', 'running a game'], 'red' if 1 in hl else 'card', 8.4)
    o += label_box(260, 14, 90, 36, ['Kernel', 'IRQ handler'], 'blue' if 2 in hl else 'card', 8.4)
    o += label_box(130, 74, 100, 36, ['bash', 'waiting for a key'], 'acc' if 3 in hl else 'card', 8.4)
    o += label_box(260, 74, 90, 36, ['Scheduler'], 'blue' if 4 in hl else 'card', 8.6)
    return o + extra + cap(msg[0], msg[1], 'blue', y=150, h=44)
ia = irq([1], ('A game is using the CPU core.', 'bash is asleep, waiting for your next key.'))
ib = irq([0, 1], ('You press a key: the keyboard raises an interrupt.', 'An electrical signal tells the CPU “stop, I have data”.'), arrow(100, 32, 128, 32, 'amber', 2.2))
ic = irq([1, 2], ('The CPU pauses the game and jumps into the kernel.', 'A short handler reads the key (interrupt context).'), arrow(230, 32, 258, 32, 'blue', 2.2))
id_ = irq([2, 3, 4], ('The kernel hands the key to the terminal and wakes bash.', 'The scheduler marks bash as ready to run.'), arrow(304, 52, 304, 72, 'blue', 2) + arrow(258, 92, 232, 92, 'blue', 2))
ie = irq([1, 3], ('Back to the game within microseconds.', 'bash runs on its next turn. Nothing is lost.'), '')
s4 = anim_one('Real-time scenario 4 · advanced', 'You press a key: an interrupt, step by step',
              'How does bash notice your key press when another program is using the CPU? Hardware interrupts. Simplified, but this is the real sequence.',
              'Hardware interrupts', 'A key press raises an interrupt; the CPU pauses a game, runs a kernel handler, wakes bash through the scheduler, then resumes the game.', [ia, ib, ic, id_, ie],
              ['A game is running on the CPU core. bash is not running at all: it is asleep in the kernel, waiting for input.',
               'You press a key. The keyboard controller raises an <b>interrupt</b>, a hardware signal to the CPU.',
               'The CPU saves what the game was doing and jumps to the kernel’s interrupt handler, which quickly reads the key code. This runs in <b>interrupt context</b>: fast and short.',
               'The kernel passes the key to the terminal layer and marks bash as runnable. The <b>scheduler</b> will give it a turn.',
               'The CPU returns to the game. Moments later bash runs and shows your character. The same mechanism handles network packets, disk completions and the timer tick. Count them in <code>/proc/interrupts</code>.'],
              hid='scenario-interrupt')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What the kernel does while <code>ls</code> runs</h2>
  <p>Left: the terminal. Right: bash and ls (user space) asking the kernel (kernel space) for everything. The dashed line is the wall between them.</p>
''' + two + '''
  <p>Four real-time scenarios: the scheduler sharing one CPU, memory protection when an app crashes, one kernel powering very different devices, and a hardware interrupt.</p>
''' + s1 + s2 + s3 + s4 + dissect('Layer by layer: dissect <code>ls</code>',
    'The animation showed bash, ls and the kernel. A real Linux system has a few more layers in between. Open each one: why it exists, how it works, where it lives on disk, where you meet it at work, and a real command that reveals it.', [
    dict(key='shell', name='Shell (bash)', sub='reads your command',
         why='Someone has to understand the text you typed and decide which program to run.',
         how='bash splits <code>ls</code> into words, sees it is not a builtin, searches PATH and asks the kernel to start <code>/usr/bin/ls</code>.',
         impl='<code>/usr/bin/bash</code>, from the GNU project.', used='Every terminal session and almost every automation script.',
         cmd='type ls'),
    dict(key='prog', name='Program: ls', sub='the tool that lists',
         why='Each job is done by a small specialised program, the Unix idea from 1969.',
         how='ls asks for the names in a folder, sorts them and prints them. It never reads the disk directly.',
         impl='<code>/usr/bin/ls</code> from GNU coreutils, a compiled C program.', used='Many thousands of times a day by every Linux user.'),
    dict(key='libc', name='C library (glibc)', sub='the polite translator',
         why='Making raw system calls is fiddly. Almost every program uses a shared library of ready-made functions that make the calls for it.',
         how='ls calls library functions such as <code>opendir()</code> and <code>readdir()</code>; glibc turns them into the real system calls.',
         impl='<code>libc.so.6</code> in <code>/lib/x86_64-linux-gnu/</code>, shared by nearly every program. <code>ldd</code> shows which libraries a program needs.',
         used='Under almost every Linux program. (Alpine Linux uses a different one, musl: Lesson 1.3.)',
         cmd='ldd /usr/bin/ls | grep libc'),
    dict(key='sys', name='System call interface', sub='the only door into the kernel',
         why='User programs must never control hardware directly. One guarded doorway keeps them safe from each other.',
         how='The CPU switches from user mode to kernel mode, the kernel does the work, and switches back. ls passes through this door well over a hundred times.',
         impl='Part of the kernel: a table of a few hundred numbered calls (openat, getdents64, write, execve…).',
         used='Debugging with <code>strace</code>: “which file is this program actually opening?”',
         cmd='strace -e trace=openat,getdents64 ls 2>&1 >/dev/null | tail -3'),
    dict(key='kernel', name='Kernel: file-system code', sub='turns names into disk blocks',
         why='Different disks use different formats (ext4, xfs, FAT). Programs should not need to know which.',
         how='The kernel’s virtual file system (VFS) passes the request to the right file-system driver, here ext4, which knows where the folder’s entries sit on disk, often already cached in RAM.',
         impl='Inside the kernel image <code>/boot/vmlinuz-…</code>, or as a module in <code>/lib/modules/</code>.',
         used='Every file operation on every Linux machine. Admins choose and tune file systems in Module 15.',
         cmd='df -T ~ | tail -1'),
    dict(key='hw', name='Hardware', sub='disk, CPU, RAM',
         why='Data has to physically live somewhere and instructions have to run on something.',
         how='The disk driver sends commands to the SSD (or a virtual disk in the cloud) and the data comes back into RAM.',
         impl='Real or virtual devices; the kernel shows them as block devices such as <code>/dev/vda</code> or <code>/dev/nvme0n1</code>.',
         used='Choosing cloud VM sizes, adding disks, replacing failed drives (Module 15).',
         cmd='lsblk -d -o NAME,SIZE,TYPE | head -3'),
]) + qc('Which layer does <code>strace</code> let you watch?', 'The system call interface: every request a program makes to the kernel.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Why this knowledge pays off at work</h2>
''' + usecase(term(8, 14, 104, 62, [('Killed', 'err'), ('$ dmesg | tail -1', 'prompt'), ('Out of memory:', 'acc')], title='server', size=6.4, step=11),
              '1. “My job was killed!”: reading the kernel’s mind',
              'A data pipeline on a server suddenly dies with the word “Killed”. A developer who knows the kernel checks its log and sees the out-of-memory killer stopped the job. Fix: more memory or a smaller batch, not random restarts.',
              ['Job dies', '*Kernel log (dmesg)', 'OOM found', 'Right fix']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ strace -e openat app', 'prompt'), ('openat("/etc/app.yml")', 'out'), ('= -1 ENOENT', 'err')], title='debug', size=5.8, step=11),
    '2. Which config file is this program reading?',
    'An app ignores your settings. <code>strace</code> shows every file it asks the kernel to open, revealing it reads a different path. A classic production debugging trick.',
    ['App misbehaves', '*strace system calls', 'Wrong path seen']) + '\n' + usecase(
    ''.join(server(10 + k * 36, 16, 30, 50, None, 'blue', leds=3) for k in range(3)),
    '3. Choosing the right server size',
    'Knowing that the kernel shares CPU cores and RAM between processes helps you size cloud servers sensibly: how many cores for parallel jobs, how much RAM so nothing is killed.',
    ['Workload', '*cores + RAM', 'Cloud VM size']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Docker', 'container'], 'blue', 9),
    '4. Containers are a kernel feature',
    'Docker containers are not small virtual machines. They are ordinary processes that the Linux kernel isolates (namespaces) and limits (cgroups). Module 20 shows how.',
    ['docker run', '*kernel namespaces + cgroups', 'isolated app']) + '\n' + usecase(
    phone(44, 14, 32, 60, text='5.x'),
    '5. Phones, cars and IoT',
    'Embedded engineers configure and build the Linux kernel for devices such as phones, car dashboards and smart meters, choosing only the drivers the hardware needs.',
    ['Device hardware', '*custom kernel build', 'Product']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Commands that ask the kernel and the shell about themselves. All were really run; on your machine names and numbers will differ.', [
    dict(level='b', title='Which kernel am I running?', scenario='A bug report asks for your kernel version. You need it in one line.',
         cmd='uname -sr', explain='<code>uname</code> prints system information from the kernel: <code>-s</code> kernel name, <code>-r</code> kernel release. Add <code>-m</code> for the CPU architecture.'),
    dict(level='b', title='Is this command part of the shell or a separate program?', scenario='You wonder why <code>cd</code> has no file in /usr/bin while <code>ls</code> does.',
         cmd='type cd ls', explain='<code>type</code> asks bash how it would run a name. Builtins live inside bash; others are program files that the kernel must start.'),
    dict(level='i', title='How many CPU cores and how much RAM, straight from the kernel', scenario='Before running a heavy job you want to know the machine’s size without any GUI.',
         cmd='echo "cores: $(nproc), RAM: $(awk \'/MemTotal/ {printf "%.1f GB", $2/1048576}\' /proc/meminfo)"',
         explain='<code>/proc/meminfo</code> is not a real file: the kernel generates it when you read it. <code>awk</code> picks the MemTotal line and converts kB to GB.'),
    dict(level='a', title='Count the system calls a command makes', scenario='You want proof that even a tiny command talks to the kernel a lot.',
         cmd='strace -c ls 2>&1 >/dev/null | tail -1',
         explain='<code>strace -c</code> counts every system call and prints a summary on stderr; <code>2>&amp;1 >/dev/null</code> sends that summary into the pipe and throws away ls’s own output. Here <code>ls</code> made well over a hundred calls to list one folder. (strace must be installed: <code>sudo apt install strace</code>.)'),
], extra=build_up('how many processes are running right now?', 'Kabir wants to know how busy the machine is, using only what the kernel shows in /proc. Build the answer one stage at a time.', '', [
    ('ls /proc | head -5', 'Look first: /proc is a virtual folder made by the kernel. Each numbered folder is one running process.'),
    ("ls /proc | grep -E '^[0-9]+$' | head -3", 'Keep only names made of digits: those are process IDs.'),
    ("ls /proc | grep -E '^[0-9]+$' | wc -l", 'Count them.'),
    ('echo "Processes running: $(ls /proc | grep -E \'^[0-9]+$\' | wc -l)"', 'Label it: a finished health-check line. (Your number will be different every time.)'),
], level='i')) + which('Questions about the OS itself, and the command that answers each.', [
    ('Know the kernel version', 'uname -r', 'Release of the running kernel.', 'Confusing it with the distribution version.'),
    ('Know the distribution and version', 'cat /etc/os-release', 'Name and version of the distro.', 'Using <code>uname</code>, which knows only the kernel.'),
    ('Know which shell you are using', 'echo $SHELL', 'Your login shell (set in /etc/passwd).', 'Expecting it to change after you start another shell; use <code>ps -p $$</code> for the current one.'),
    ('See if a name is a builtin or a program', 'type cd', 'Shows builtin, alias, function or file path.', '<code>which</code> does not know builtins or aliases.'),
    ('See all system calls of a program', 'strace ls', 'Lists every request to the kernel.', 'Running it on a busy production process without permission: it slows it down.'),
    ('Read kernel messages (drivers, OOM)', 'sudo dmesg | tail', 'The kernel’s own log.', 'Looking only in the app’s log when the kernel killed it.'),
    ('List loaded kernel modules', 'lsmod', 'Drivers and features currently loaded.', 'Removing a module you do not understand.'),
]) + '''
''' + puzzle_answer('The <b>kernel</b> reads the folder. bash asks the kernel to start ls; ls asks the kernel (through the C library and system calls such as <code>openat</code> and <code>getdents64</code>) for the folder’s entries; the kernel’s file-system code fetches them from the disk or its cache. The proof is one command: <code>strace ls</code> prints every request ls makes to the kernel, as you saw in the dissection above.') + qc('Your phone runs Android. Name its kernel.', 'Linux. Android uses the Linux kernel with Google’s own user space on top.') + '''
</section>
'''

cmap = concept_map(
    [('1.1', 'Computer basics', 'CPU, RAM, disk, files, servers')],
    ['what an OS does', 'kernel vs shell', 'user space, kernel space, system calls', 'kernel designs', 'Unix → GNU → Linux story'],
    [('1.3', 'Distributions', 'kernel + tools = Ubuntu, RHEL…'), ('1.6', 'Terminal and prompt', 'using the shell'), ('11.1', 'Processes', 'what the kernel runs'), ('20.1', 'System calls in depth', 'strace, modules')],
    'The kernel and the shell come back in almost every module: processes (11), permissions (9), storage (15) and containers (20) are all kernel features.')
body = cmap + (story.replace('  <div class="story">', before('<a href="../01-before-you-start-computer-basics-files-servers/">Lesson 1.1</a> (CPU, RAM, disk, files, servers). Nothing else.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
