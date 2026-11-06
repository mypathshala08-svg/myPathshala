#!/usr/bin/env python3
"""Builds courses/linux/glossary/index.html (Linux glossary with 'Behind the screen' notes).

Run from the site root:  python3 tools/authoring/src/linux/glossary/make_glossary.py
Each term: T(term, group, lesson "m.l", simple words, behind the screen, flow="a → b → c", ex="command", aka="")
Lesson links are resolved from courses/linux/course.json; the page turns them into links only for
lessons that are live (read from data/courses/linux.js at view time).
"""
import json, html, re, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
E = lambda s: html.escape(s, quote=True)

GROUPS = [
    ("basics", "Linux basics and boot"),
    ("fs", "Files and the directory tree"),
    ("storage", "Disks, file systems and memory"),
    ("shell", "The shell, streams and pipes"),
    ("text", "Text processing and regex"),
    ("users", "Users, groups and sudo"),
    ("perms", "Permissions"),
    ("proc", "Processes and signals"),
    ("services", "Services, scheduling and logs"),
    ("pkg", "Packages and archives"),
    ("net", "Networking and SSH"),
    ("sec", "Security and kernel internals"),
]

TERMS = []
def T(term, g, ref, simple, behind, flow=None, ex=None, aka=None):
    TERMS.append(dict(term=term, g=g, ref=ref, simple=simple, behind=behind, flow=flow, ex=ex, aka=aka))

# ------------------------------------------------------------------ basics
T("Operating system (OS)", "basics", "1.2",
  "The software that runs the computer: it shares the CPU, memory, disks and network between all your programs.",
  "An OS has two big parts: the <b>kernel</b> (talks to hardware) and the <b>user-space</b> tools you use (shell, commands, desktop). Linux, strictly, is the kernel; Ubuntu or RHEL is a whole OS built around it.")
T("Kernel", "basics", "1.2",
  "The core program of Linux. It controls the hardware and decides which program gets the CPU, memory and disk next.",
  "The kernel runs in a protected CPU mode (kernel space). Your programs run in user space and cannot touch hardware directly; they ask the kernel through <b>system calls</b>. One kernel, many programs, all kept apart from each other.",
  flow="app calls read() → CPU switches to kernel mode → kernel asks the disk driver → data copied into the app's memory → back to user mode",
  ex="uname -r")
T("Shell", "basics", "1.2",
  "The program that reads the commands you type and runs them. On most Linux systems it is <code>bash</code>.",
  "The shell is just an ordinary program. For every line you type it splits words, does expansions (<code>$HOME</code>, <code>*.txt</code>, <code>~</code>), finds the command (alias → function → builtin → a file in <code>PATH</code>), then <b>forks</b> a child and <b>execs</b> the program in it, waits, and prints the prompt again.",
  flow="you type ls -l *.txt → split into words → *.txt expanded to real names → /usr/bin/ls found via PATH → fork + exec → wait → prompt",
  ex="echo $SHELL; ps -p $$", aka="bash, zsh, sh")
T("Terminal (terminal emulator)", "basics", "1.6",
  "The window where you type. It shows text and sends your key presses to the shell.",
  "The terminal and the shell are two different programs joined by a <b>pseudo-terminal (pty)</b>, a kernel device like <code>/dev/pts/0</code>. Keys go terminal → pty → shell; the shell's output goes back the same way and the terminal draws it. Closing the window sends <b>SIGHUP</b> to the shell.",
  flow="key press → terminal app → /dev/pts/N → shell reads it → output → /dev/pts/N → terminal draws text",
  ex="tty", aka="GNOME Terminal, Windows Terminal, PuTTY")
T("Console / virtual console", "basics", "1.6",
  "A text-only login screen provided by the machine itself, without any window app.",
  "Linux gives you several virtual consoles (<code>/dev/tty1</code>…<code>tty6</code>). On a desktop, <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>F3</kbd> switches to one. Servers in a data centre are often reached through a remote console when SSH is broken.",
  ex="who")
T("Command, option and argument", "basics", "1.6",
  "In <code>ls -l /etc</code>: <code>ls</code> is the command, <code>-l</code> an option (changes how it works), <code>/etc</code> an argument (what it works on).",
  "The shell hands the program an array of strings called <b>argv</b>: <code>argv[0]=\"ls\"</code>, <code>argv[1]=\"-l\"</code>, <code>argv[2]=\"/etc\"</code>. Options are not magic: each program reads argv and decides what <code>-l</code> means, which is why options differ between commands.",
  ex="ls -l /etc")
T("Prompt", "basics", "1.6",
  "The text before your cursor, like <code>riya@laptop:~$</code>. <code>$</code> means a normal user, <code>#</code> means root.",
  "The prompt is built from the shell variable <code>PS1</code> each time the shell is ready. <code>\\u</code> = user, <code>\\h</code> = host, <code>\\w</code> = current folder.",
  ex="echo \"$PS1\"", aka="PS1")
T("Distribution (distro)", "basics", "1.3",
  "A complete Linux OS: the kernel plus tools, a package manager, an installer and default settings. Ubuntu, Debian, Fedora, RHEL, Rocky, Arch.",
  "All distros share the same Linux kernel family and mostly the same GNU tools. What really differs: the <b>package format</b> (.deb vs .rpm), the package manager (apt vs dnf), release cycle, default configs and support period.",
  ex="cat /etc/os-release")
T("GNU", "basics", "1.2",
  "A free-software project whose tools (bash, ls, cp, grep, gcc) make up much of what you use on Linux.",
  "Linus Torvalds wrote the kernel in 1991; the GNU project had already written most of the user-space tools. Together they formed a full free OS, which is why some people say <b>GNU/Linux</b>.")
T("Open source and the GPL", "basics", "1.4",
  "Open source means anyone may read, change and share the code. The Linux kernel uses the GNU GPL version 2 licence.",
  "The GPL lets you use and modify the code freely, but if you <b>distribute</b> a modified version you must also share its source code under the same licence. This rule is why improvements by companies flow back into Linux.")
T("Unix", "basics", "1.4",
  "The operating system from Bell Labs (1969) whose design Linux follows: small tools, everything is a file, a shell to join them.",
  "Linux is <b>Unix-like</b>, not Unix code: it was written from scratch but follows the same ideas and the POSIX standard, so most Unix skills and scripts carry over.")
T("WSL (Windows Subsystem for Linux)", "basics", "1.5",
  "A Windows feature that runs a real Linux (e.g. Ubuntu) inside Windows, without dual boot.",
  "WSL 2 runs a real Linux kernel inside a lightweight virtual machine managed by Windows. Your Windows drives appear in Linux under <code>/mnt/c</code>; Linux files are reachable from Windows at <code>\\\\wsl$</code>.",
  ex="wsl --install   (in Windows PowerShell)")
T("Virtual machine (VM)", "basics", "1.5",
  "A whole computer simulated in software (VirtualBox, VMware, a cloud server), with its own OS.",
  "A <b>hypervisor</b> gives each VM virtual CPUs, RAM and disks, using CPU features (Intel VT-x, AMD-V) so guest code runs at near-native speed. A cloud server like AWS EC2 is a VM in someone else's data centre.")
T("Boot loader (GRUB)", "basics", "17.1",
  "The small program that starts first after the firmware and loads the Linux kernel.",
  "GRUB reads its menu from <code>/boot/grub/grub.cfg</code>, loads the kernel file (<code>vmlinuz</code>) and the <b>initramfs</b> into RAM, and passes a kernel command line (e.g. <code>root=UUID=…</code>).",
  flow="power on → UEFI/BIOS → GRUB → kernel + initramfs → real root mounted → systemd (PID 1) → services → login",
  ex="cat /proc/cmdline")
T("initramfs", "basics", "17.1",
  "A tiny temporary file system loaded into RAM at boot, with just enough drivers to find and mount the real disk.",
  "The kernel unpacks it, runs its <code>/init</code>, which loads disk/RAID/LVM/encryption drivers, mounts the real root file system and then hands over to systemd.",
  ex="ls /boot")
T("systemd / init (PID 1)", "basics", "17.2",
  "The first program the kernel starts. It starts every other service and keeps them running.",
  "It always has process ID 1. It reads unit files, starts services in parallel based on dependencies, puts each service in its own cgroup, collects logs (journald), and adopts orphan processes. If PID 1 dies, the kernel panics.",
  ex="ps -p 1 -o comm=")

# ------------------------------------------------------------------ fs
T("Everything is a file", "fs", "2.1",
  "Linux shows most things as files: documents, folders, disks, terminals, even running processes.",
  "The kernel gives one interface (open, read, write, close) for all of them. A program that can read a file can also read <code>/dev/sda</code>, a pipe, a socket or <code>/proc/cpuinfo</code>; the kernel routes each call to the right driver or file system.",
  ex="cat /proc/cpuinfo | head")
T("Root directory ( / )", "fs", "2.1",
  "The top of Linux's single folder tree. Every file is somewhere under <code>/</code>; there are no C: or D: drives.",
  "Other disks and partitions are <b>mounted</b> onto folders inside this one tree (for example a second disk at <code>/data</code>), so a path alone does not tell you which disk it lives on; <code>df</code> does.",
  ex="ls /; df -h /")
T("File System Hierarchy (FHS)", "fs", "2.1",
  "The standard map of which folder holds what: <code>/etc</code> configs, <code>/home</code> users, <code>/var</code> logs and data, <code>/usr</code> programs, <code>/tmp</code> temporary files.",
  "Because distros follow the FHS, a log is in <code>/var/log</code> on almost any server and an admin can find their way around a machine they have never seen.",
  ex="man hier")
T("/etc", "fs", "2.1",
  "Where system-wide configuration files live, as plain text: <code>/etc/passwd</code>, <code>/etc/hosts</code>, <code>/etc/ssh/sshd_config</code>.",
  "Programs read these text files at start-up (or on reload). That is why editing a file in <code>/etc</code> often needs a <code>systemctl restart</code> or <code>reload</code> before it takes effect.")
T("/var", "fs", "2.1",
  "Variable data that grows while the system runs: logs (<code>/var/log</code>), caches, mail queues, databases.",
  "\"Disk full\" on servers is very often <code>/var/log</code> or <code>/var/lib/docker</code> filling up. <code>du -sh /var/*</code> is the first check.",
  ex="du -sh /var/* 2>/dev/null | sort -h")
T("/tmp", "fs", "2.1",
  "A shared folder for temporary files. Anyone may write there; it may be emptied at reboot.",
  "Its permission is <code>drwxrwxrwt</code>: writable by all, plus the <b>sticky bit</b> (<code>t</code>) so you can delete only your own files. On many systems it is a <code>tmpfs</code> that lives in RAM.",
  ex="ls -ld /tmp")
T("/usr, /bin and /sbin", "fs", "2.1",
  "<code>/usr</code> holds installed programs and libraries. <code>/bin</code> has everyday commands; <code>/sbin</code> admin commands.",
  "On modern Ubuntu, Debian, Fedora and RHEL, <code>/bin</code> is only a symbolic link to <code>/usr/bin</code> (the \"merged /usr\"), so both paths reach the same files.",
  ex="readlink -f /bin")
T("/home and ~", "fs", "2.3",
  "Each user's personal folder, like <code>/home/riya</code>. <code>~</code> is a shortcut for your own home.",
  "<code>~</code> is replaced by the <b>shell</b> with the value of <code>$HOME</code> before the command runs; the program receives the full path. The home folder of each user is the 6th field of <code>/etc/passwd</code>. root's home is <code>/root</code>.",
  ex="echo ~; echo $HOME")
T("/dev", "fs", "2.4",
  "Device files: <code>/dev/sda</code> (a disk), <code>/dev/null</code>, <code>/dev/tty</code>, <code>/dev/random</code>.",
  "These are not stored on disk. The kernel's <b>devtmpfs</b> and the <b>udev</b> service create them as hardware appears. Each has a major/minor number that tells the kernel which driver handles reads and writes.",
  ex="ls -l /dev/null /dev/sda 2>/dev/null")
T("/proc", "fs", "20.2",
  "A virtual folder through which the kernel shows live information: one folder per process, CPU, memory, settings.",
  "Nothing in <code>/proc</code> is on disk. When you <code>cat /proc/meminfo</code>, the kernel generates the text at that moment. <code>ps</code>, <code>top</code> and <code>free</code> simply read these files.",
  flow="cat /proc/meminfo → open() → procfs asks the memory manager → text built on the fly → printed",
  ex="cat /proc/meminfo | head -3")
T("/sys", "fs", "20.2",
  "A virtual folder showing devices, drivers and kernel settings as small files.",
  "sysfs mirrors the kernel's device model. Writing to some files changes the kernel live, e.g. LED brightness or a disk's I/O scheduler. cgroup v2 lives at <code>/sys/fs/cgroup</code>.",
  ex="ls /sys/class/net")
T("Path: absolute and relative", "fs", "2.3",
  "An <b>absolute</b> path starts at <code>/</code> (<code>/home/riya/notes.txt</code>). A <b>relative</b> path starts from where you are (<code>notes.txt</code>, <code>../docs</code>).",
  "The kernel resolves a path one name at a time: from <code>/</code> for an absolute path, or from the process's current directory for a relative one, looking each name up in the directory it is in, checking <code>x</code> permission on every folder along the way.",
  flow="/home/riya/a.txt → look up 'home' in / → 'riya' in home → 'a.txt' in riya → inode found → open")
T("Current working directory", "fs", "2.2",
  "The folder you are \"in\" right now. <code>pwd</code> prints it; <code>cd</code> changes it.",
  "The kernel stores a current directory for each process. That is why <code>cd</code> must be a <b>shell builtin</b>: a separate <code>cd</code> program would change only its own directory and then exit, leaving the shell where it was.",
  ex="pwd; type cd", aka="pwd")
T(". and ..", "fs", "2.3",
  "<code>.</code> means this folder, <code>..</code> means the parent folder.",
  "They are real entries inside every directory, pointing to the directory itself and to its parent. That is why a new folder already has a link count of 2.",
  ex="ls -la")
T("Hidden file (dotfile)", "fs", "2.4",
  "A file whose name starts with a dot, like <code>.bashrc</code>. <code>ls</code> hides it unless you add <code>-a</code>.",
  "There is nothing special about it in the kernel: it is only a convention followed by <code>ls</code>, file managers and globbing (<code>*</code> does not match a leading dot). Config files use it to stay out of the way.",
  ex="ls -a ~")
T("File types", "fs", "2.4",
  "The first letter of <code>ls -l</code> shows the type: <code>-</code> file, <code>d</code> directory, <code>l</code> link, <code>c</code>/<code>b</code> device, <code>p</code> pipe, <code>s</code> socket.",
  "The type is stored in the file's inode, not in its name. Linux does not care about extensions: <code>file</code> looks at the first bytes (\"magic numbers\") to guess the content.",
  ex="file /bin/ls /etc/hosts")
T("Inode", "fs", "10.1",
  "The record that describes a file: owner, permissions, size, timestamps and where its data blocks are. It does <b>not</b> contain the file's name.",
  "A directory is a list of <i>name → inode number</i> pairs. Opening a file means finding the inode through those names. Disks can run out of inodes even with free space left (millions of tiny files).",
  flow="name 'notes.txt' → directory entry → inode 1204253 → permissions checked → data blocks read",
  ex="ls -i notes.txt; stat notes.txt; df -i")
T("Hard link", "fs", "10.2",
  "A second name for the same file. Both names are equal; deleting one leaves the other working.",
  "<code>ln a b</code> adds a new directory entry pointing to the <b>same inode</b> and raises its link count. Data is freed only when the count reaches 0 and no process has it open. Hard links cannot cross file systems or (normally) point to directories.",
  ex="ln a.txt b.txt; ls -li a.txt b.txt")
T("Symbolic (soft) link", "fs", "10.2",
  "A shortcut file that contains a path to another file. Breaks if the target is moved or deleted.",
  "A symlink has its own inode whose content is just the target path. The kernel follows it while resolving a path. It can point anywhere, across disks, even to something that does not exist yet (a \"dangling\" link).",
  ex="ln -s /var/log/nginx logs; ls -l logs")
T("File descriptor (fd)", "fs", "5.1",
  "A small number a program uses for each open file: 0 = input, 1 = output, 2 = errors, 3+ = files it opened.",
  "When a program opens a file, the kernel adds an entry to that process's descriptor table and returns its number. Every later read or write uses the number. Redirection works by changing what 0, 1 and 2 point to.",
  ex="ls -l /proc/$$/fd")
T("/dev/null", "fs", "5.2",
  "A \"black hole\" device: whatever you write to it disappears; reading from it gives nothing.",
  "It is a character device (<code>c 1,3</code>). Its driver accepts every write and throws the data away, and returns end-of-file on every read. <code>2>/dev/null</code> hides error messages.",
  ex="find / -name '*.conf' 2>/dev/null")
T("Deleted but still open file", "fs", "18.4",
  "Why disk space does not come back after <code>rm</code> of a huge log: a running program still has it open.",
  "<code>rm</code> only removes the name. The inode and its data stay until the last open descriptor is closed. Restart (or signal) the program, or truncate the file instead of deleting it.",
  ex="sudo lsof +L1")

# ------------------------------------------------------------------ storage
T("Block device", "storage", "15.1",
  "A disk-like device read and written in blocks: <code>/dev/sda</code>, <code>/dev/nvme0n1</code>, <code>/dev/vda</code>.",
  "The kernel puts a block layer between file systems and drivers that queues, merges and schedules requests, and caches data in the page cache.",
  ex="lsblk")
T("Partition and partition table", "storage", "15.1",
  "A separate section of a disk (<code>/dev/sda1</code>, <code>/dev/sda2</code>), each usable on its own.",
  "The start and end of each partition are written in a table at the beginning of the disk: <b>GPT</b> (modern, many partitions, very large disks) or <b>MBR</b> (old, max 4 primary, 2 TiB).",
  ex="lsblk -f; sudo fdisk -l")
T("File system (ext4, xfs)", "storage", "15.2",
  "The way files and folders are laid out on a partition. ext4 is the common default; xfs is the default on RHEL.",
  "<code>mkfs</code> writes empty structures onto the partition: a <b>superblock</b>, inode tables, free-space bitmaps and a <b>journal</b>. Until a partition has a file system, it cannot store files.",
  ex="lsblk -f")
T("Journaling", "storage", "15.2",
  "A safety log the file system writes before changing its structures, so a power cut does not corrupt it.",
  "ext4 first writes the planned metadata change to the journal, then makes it. After a crash, it replays or discards journal entries in seconds instead of checking the whole disk.")
T("Superblock", "storage", "15.2",
  "The header of a file system: its size, block size, inode count, state and features.",
  "If it is damaged the file system cannot be mounted, so ext4 keeps backup copies at known places on disk that <code>fsck</code> can use.",
  ex="sudo dumpe2fs -h /dev/sda1 | head")
T("Mount and mount point", "storage", "15.3",
  "Mounting attaches a file system to a folder (the mount point) so its files appear there.",
  "The kernel keeps a mount table. When path lookup reaches a mount point it continues inside the mounted file system. Whatever was in the folder before is hidden, not deleted, until you unmount.",
  ex="findmnt; sudo mount /dev/sdb1 /data")
T("/etc/fstab", "storage", "15.3",
  "The list of file systems to mount automatically at boot.",
  "Each line: device (best by <code>UUID=</code>), mount point, type, options, dump, fsck order. systemd turns every line into a <code>.mount</code> unit at boot. A typo can stop the machine booting, so test with <code>sudo mount -a</code> first.",
  ex="cat /etc/fstab")
T("UUID", "storage", "15.3",
  "A long unique ID given to a file system when it is created.",
  "Device names like <code>/dev/sdb</code> can change when disks are added; the UUID does not. That is why fstab uses <code>UUID=…</code>.",
  ex="blkid")
T("LVM (PV, VG, LV)", "storage", "15.5",
  "Logical Volume Manager: pools disks together and cuts flexible \"virtual partitions\" that can grow later.",
  "<b>PV</b> = a disk or partition prepared for LVM. <b>VG</b> = a pool of PVs, divided into extents (4 MiB by default). <b>LV</b> = a volume made of extents. The kernel's device-mapper maps each LV block to a real disk block, so an LV can grow across disks while mounted.",
  flow="disks /dev/sdb + /dev/sdc → pvcreate → vgcreate datavg → lvcreate 50G → mkfs → mount → lvextend later",
  ex="sudo pvs; sudo vgs; sudo lvs")
T("Swap", "storage", "15.4",
  "Disk space used as overflow when RAM is full.",
  "The kernel moves memory pages that have not been used for a while to swap and brings them back when needed. It prevents crashes, but heavy swapping (\"thrashing\") makes everything very slow. <code>vm.swappiness</code> tunes how eager it is.",
  ex="swapon --show; free -h")
T("Page cache (buff/cache)", "storage", "15.4",
  "Spare RAM the kernel uses to keep recently read files. It is why \"free\" memory looks small.",
  "Reading a file the second time is much faster because it comes from RAM. The cache is given back instantly when programs need memory, so look at the <b>available</b> column of <code>free</code>, not <b>free</b>.",
  ex="free -h")
T("Virtual memory", "storage", "11.5",
  "Each process believes it has its own large private memory. The kernel maps it onto real RAM (and swap).",
  "Memory is managed in pages (usually 4 KiB) through page tables. <b>VSZ</b> in <code>ps</code> is the size of the address space; <b>RSS</b> is how much is really in RAM now.",
  ex="ps -o pid,vsz,rss,comm -p $$")
T("OOM killer", "storage", "18.4",
  "When RAM and swap run out, the kernel kills a process to save the system.",
  "It picks the process with the highest <code>oom_score</code> (mostly the biggest memory user) and sends it SIGKILL. The kernel log then shows \"Out of memory: Killed process …\". A database or Java app vanishing with no error is a typical sign.",
  ex="sudo dmesg | grep -i 'out of memory'")

# ------------------------------------------------------------------ shell
T("Builtin vs external command", "shell", "12.1",
  "A builtin (<code>cd</code>, <code>echo</code>, <code>export</code>) runs inside the shell. An external command (<code>ls</code>, <code>grep</code>) is a separate program file.",
  "Builtins exist when the work must change the shell itself (current folder, variables) or for speed: no fork or exec is needed.",
  ex="type cd ls echo")
T("PATH", "shell", "12.1",
  "The list of folders where the shell looks for commands, separated by <code>:</code>.",
  "For a command without a <code>/</code>, the shell searches each PATH folder from left to right and runs the first match; it remembers the result in a hash table. \"command not found\" (exit code 127) means no folder had it. The current folder is not in PATH, which is why you type <code>./script.sh</code>.",
  flow="you type python3 → /usr/local/sbin? no → /usr/local/bin? no → /usr/bin/python3 yes → exec",
  ex="echo $PATH; which python3")
T("Shell variable vs environment variable", "shell", "12.1",
  "A shell variable exists only in your current shell. An environment variable is also passed to every program you start.",
  "<code>export</code> marks a variable so the shell copies it into the environment of each child at <code>exec</code> time. Children get a <b>copy</b>; nothing a child changes ever comes back to the parent.",
  ex="X=1; bash -c 'echo [$X]'; export X; bash -c 'echo [$X]'",
  aka="export, env")
T("Alias", "shell", "12.3",
  "A short name for a longer command, e.g. <code>alias ll='ls -alF'</code>.",
  "The shell replaces the first word of a command with the alias text before running it. Aliases are not used in scripts by default and are forgotten when the shell exits unless saved in <code>~/.bashrc</code>.",
  ex="alias; type ll")
T("History", "shell", "12.3",
  "The list of commands you typed before. Arrow keys, <code>history</code>, <code>!!</code> and <kbd>Ctrl</kbd>+<kbd>R</kbd> reuse them.",
  "bash keeps history in memory and writes it to <code>~/.bash_history</code> when the shell exits, so two open terminals can overwrite each other's history unless <code>histappend</code> is set.",
  ex="history | tail -5")
T("Startup files (.bashrc, .profile)", "shell", "12.2",
  "Files bash runs when it starts, to set your PATH, aliases and prompt.",
  "A <b>login</b> shell (SSH, console) reads <code>/etc/profile</code>, then the first of <code>~/.bash_profile</code>, <code>~/.bash_login</code>, <code>~/.profile</code>. An interactive <b>non-login</b> shell (a new terminal tab) reads <code>~/.bashrc</code>. Ubuntu's <code>~/.profile</code> also loads <code>.bashrc</code>.",
  ex="source ~/.bashrc")
T("source (.) vs ./script", "shell", "12.5",
  "<code>source file</code> runs a file inside your current shell. <code>./script.sh</code> runs it in a new child shell.",
  "With <code>source</code>, variables and <code>cd</code> made by the file stay in your shell. With <code>./script.sh</code>, the kernel starts a new process; its changes vanish when it exits.",
  ex="source ~/.bashrc")
T("Shebang (#!)", "shell", "12.5",
  "The first line of a script, like <code>#!/bin/bash</code>, saying which program should run it.",
  "When you run <code>./backup.sh</code>, the kernel's <code>execve</code> sees <code>#!</code>, starts <code>/bin/bash</code> and gives it the script path as an argument. The file also needs execute permission, or you get \"Permission denied\" (exit code 126).",
  flow="./backup.sh → execve() → kernel reads '#!/bin/bash' → runs /bin/bash ./backup.sh",
  ex="head -1 /usr/bin/ldd")
T("Globbing (wildcards)", "shell", "3.4",
  "Patterns like <code>*.txt</code>, <code>file?.log</code>, <code>[abc]*</code> that match file names.",
  "The <b>shell</b> expands the pattern into the matching names <i>before</i> the command runs: <code>rm *.log</code> becomes <code>rm a.log b.log</code>. The program never sees the <code>*</code>. If nothing matches, bash passes the pattern unchanged.",
  flow="rm *.log → shell reads the folder → '*.log' becomes 'a.log b.log' → rm receives two names",
  ex="echo *.txt", aka="wildcards, *, ?")
T("Brace expansion", "shell", "3.4",
  "<code>{a,b,c}</code> and <code>{1..5}</code> generate several words: <code>mkdir -p app/{src,docs,tests}</code>.",
  "It is pure text generation, done first, without looking at any files, so it works for names that do not exist yet (unlike <code>*</code>).",
  ex="echo day{1..3}.log")
T("Quoting: single vs double quotes", "shell", "12.4",
  "<code>'…'</code> keeps everything exactly as written. <code>\"…\"</code> still expands <code>$VAR</code> and <code>$( )</code> but keeps spaces together.",
  "Without quotes, the shell splits a variable's value on spaces and expands wildcards in it, so a file named <code>my file.txt</code> becomes two arguments. Quote variables: <code>\"$file\"</code>.",
  ex="name='Riya S'; echo '$name'; echo \"$name\"")
T("Expansion order", "shell", "12.4",
  "The fixed order in which bash rewrites your command line before running it.",
  "Brace → tilde, variable, arithmetic and command substitution → word splitting → filename (glob) expansion → quote removal. Knowing it explains most \"why did my command do that?\" surprises.",
  flow="cp ~/{a,b}.txt $D → brace: ~/a.txt ~/b.txt → tilde: /home/riya/… → $D replaced → split → globs → run")
T("Command substitution $( )", "shell", "5.4",
  "Puts a command's output into another command: <code>echo \"Today is $(date +%A)\"</code>.",
  "The shell runs the inner command in a subshell, captures what it prints, removes trailing newlines and pastes the text in place.",
  ex="echo \"Files: $(ls | wc -l)\"")
T("Process substitution <( )", "shell", "13.1",
  "Lets a command's output be used where a file name is expected: <code>diff <(sort a) <(sort b)</code>.",
  "bash runs the command with its output into a pipe and passes a path like <code>/dev/fd/63</code> to the outer command, which opens it as if it were a file.",
  ex="echo <(true)")
T("Subshell ( )", "shell", "13.1",
  "Commands inside <code>( )</code> run in a copy of the shell. Changes inside do not affect your shell.",
  "bash forks a child copy. <code>(cd /tmp && tar czf x.tgz data)</code> leaves you in your original folder. Pipelines also run their parts in subshells.",
  ex="(cd /tmp; pwd); pwd")
T("Exit status ($?)", "shell", "5.4",
  "Every command ends with a number: 0 = success, anything else = failure. <code>$?</code> shows the last one.",
  "The program passes it to <code>exit()</code>; the kernel holds it until the parent collects it with <code>wait()</code>. Common values: 1 general error, 2 misuse, 126 not executable, 127 not found, 128+N killed by signal N (130 = Ctrl+C).",
  ex="ls /nope; echo $?")
T("Chaining: ;  &&  ||", "shell", "5.4",
  "<code>a ; b</code> always runs b. <code>a && b</code> runs b only if a succeeded. <code>a || b</code> runs b only if a failed.",
  "The shell simply checks the exit status of <code>a</code>. <code>mkdir logs && cd logs</code> never cds into a folder that failed to be created.",
  ex="make && ./app || echo 'build failed'")
T("Standard streams (stdin, stdout, stderr)", "shell", "5.1",
  "Every program starts with three channels: input (0), normal output (1) and error output (2).",
  "They are just file descriptors 0, 1 and 2, already open when the program starts, normally all pointing to your terminal. Keeping errors on a separate channel lets you save output while still seeing errors.",
  flow="keyboard → fd 0 → program → fd 1 (output) → screen ; fd 2 (errors) → screen")
T("Redirection (>, >>, <, 2>)", "shell", "5.2",
  "Send output to a file (<code>></code> overwrite, <code>>></code> append), read input from a file (<code><</code>), send errors elsewhere (<code>2></code>).",
  "Before running the program, the shell opens the file and connects it to fd 1 (or 0, or 2) using <code>dup2()</code>. The program has no idea; it just writes to fd 1. <code>></code> opens with truncate, so the file is emptied <i>before</i> the command even starts: <code>sort f > f</code> destroys f.",
  flow="ls > out.txt → shell opens out.txt (truncate) → dup2 onto fd 1 → exec ls → ls writes to fd 1 → bytes land in out.txt",
  ex="ls /etc > list.txt 2> errors.txt")
T("2>&1", "shell", "5.2",
  "Send errors to the same place as normal output.",
  "It means \"make fd 2 a copy of whatever fd 1 is <i>now</i>\". Order matters: <code>cmd > all.log 2>&1</code> puts both in the file, but <code>cmd 2>&1 > all.log</code> sends errors to the screen because fd 1 still pointed there at that moment. <code>&> all.log</code> is the bash shortcut.",
  ex="./backup.sh > run.log 2>&1")
T("Pipe ( | )", "shell", "5.3",
  "Connects the output of one command to the input of the next: <code>ps aux | grep java</code>.",
  "The kernel creates a pipe buffer (64 KiB on Linux) and the shell starts <b>all</b> commands at the same time: the writer's fd 1 and the reader's fd 0 point at the pipe. A full pipe pauses the writer; when the reader exits early (like <code>head</code>), the writer gets SIGPIPE and stops.",
  flow="cat log → [ kernel pipe buffer ] → grep ERROR → [ pipe ] → wc -l → screen",
  ex="cat access.log | grep ' 500 ' | wc -l")
T("Here-document (<<EOF)", "shell", "5.2",
  "Gives several lines of text as input to a command, written right in the script.",
  "bash collects the lines up to the end marker and feeds them to the command's stdin. With <code><<'EOF'</code> (quoted) variables inside are not expanded. <code><<<</code> (here-string) feeds a single string.",
  ex="cat <<EOF > note.txt\nHello $USER\nEOF")
T("tee", "shell", "5.3",
  "Shows output on the screen and saves it to a file at the same time.",
  "It reads stdin and writes every chunk to stdout and to each file. <code>echo text | sudo tee /etc/file</code> is the standard way to write a root-owned file, because <code>sudo echo text > /etc/file</code> redirects as <i>you</i>, not as root.",
  ex="./deploy.sh | tee deploy.log")
T("xargs", "shell", "13.2",
  "Turns lines of input into arguments for a command: <code>find . -name '*.tmp' | xargs rm</code>.",
  "It reads items from stdin and builds as few command lines as possible within the system's argument-size limit (ARG_MAX). Use <code>find -print0 | xargs -0</code> so names with spaces stay whole; <code>-P 4</code> runs 4 in parallel.",
  ex="find . -name '*.log' -print0 | xargs -0 gzip")
T("Job control (fg, bg, Ctrl+Z)", "shell", "11.4",
  "Run commands in the background (<code>&</code>), pause one (<kbd>Ctrl</kbd>+<kbd>Z</kbd>), and bring it back (<code>fg</code>) or let it continue in the background (<code>bg</code>).",
  "<kbd>Ctrl</kbd>+<kbd>Z</kbd> makes the terminal send SIGTSTP, which stops the job; <code>fg</code>/<code>bg</code> send SIGCONT. Jobs belong to that shell, so closing the terminal ends them unless you use <code>nohup</code>, <code>tmux</code> or a systemd service.",
  ex="sleep 300 &; jobs")
T("man page and sections", "shell", "2.5",
  "The built-in manual: <code>man ls</code>. Pages are grouped in sections: 1 commands, 5 file formats, 8 admin commands.",
  "The same name can exist in several sections: <code>man passwd</code> shows the command, <code>man 5 passwd</code> the format of <code>/etc/passwd</code>. <code>man -k word</code> (apropos) searches the descriptions.",
  ex="man 5 passwd")
T("Tab completion", "shell", "2.3",
  "Press <kbd>Tab</kbd> to complete a command or file name; press twice to list choices.",
  "bash's readline library looks at what you typed so far and the folder contents; the bash-completion package adds smart rules for options of commands like <code>git</code> and <code>systemctl</code>.")

# ------------------------------------------------------------------ text
T("Filter", "text", "6.2",
  "A command that reads text in, changes it, and writes text out: <code>grep</code>, <code>sort</code>, <code>cut</code>, <code>tr</code>, <code>wc</code>.",
  "Filters read stdin when no file is given and write stdout, which is what lets them be joined with pipes into a pipeline, each doing one small job.")
T("grep", "text", "6.1",
  "Prints the lines that contain a pattern: <code>grep ERROR app.log</code>.",
  "It reads input line by line and tests each line against a regular expression. Useful options: <code>-i</code> ignore case, <code>-v</code> invert, <code>-r</code> recursive, <code>-n</code> line numbers, <code>-c</code> count, <code>-w</code> whole word, <code>-E</code> extended regex. Exit status is 0 if something matched, 1 if not, which scripts use in <code>if</code>.",
  ex="grep -rn 'Exception' /var/log/myapp/")
T("Regular expression (regex)", "text", "6.6",
  "A pattern language for text: <code>^</code> start of line, <code>$</code> end, <code>.</code> any character, <code>*</code> repeat, <code>[0-9]</code> a digit.",
  "The tool compiles the pattern into a matching machine (an automaton) and runs every line through it, which is why grep can scan gigabytes quickly.",
  ex="grep -E '^[0-9]{10}$' phones.txt")
T("Basic vs extended regex (BRE / ERE)", "text", "6.6",
  "In basic regex (grep, sed) <code>+ ? | ( ) { }</code> are ordinary characters unless escaped; in extended regex (<code>grep -E</code>, <code>sed -E</code>, awk) they are special.",
  "<code>grep 'ab+'</code> looks for a literal plus; <code>grep -E 'ab+'</code> means one or more b. Most \"my regex doesn't work\" problems are this.",
  ex="grep -E '(ERROR|WARN)' app.log")
T("sed", "text", "6.4",
  "The stream editor: edits text on the fly, e.g. replace words: <code>sed 's/old/new/g' file</code>.",
  "sed reads one line into its \"pattern space\", runs your commands on it, prints it, and moves on. With <code>-i</code> it writes the result to a new temporary file and renames it over the original, so the file gets a <b>new inode</b> (hard links to the old one keep the old text).",
  ex="sed -i 's/8080/9090/g' app.conf")
T("awk", "text", "6.5",
  "A small language for column-based text: <code>awk '{print $1}' access.log</code> prints the first column.",
  "awk splits every line (record) into fields <code>$1</code>, <code>$2</code>…<code>$NF</code> using the field separator (spaces by default, <code>-F,</code> for CSV), then runs <i>pattern { action }</i> rules. <code>BEGIN</code> runs before the first line, <code>END</code> after the last, which is where totals are printed.",
  flow="line → split into $1 $2 $3 … → check pattern ($9==500) → run action (count++) → … → END prints count",
  ex="awk -F, '$3>1000 {sum+=$3} END {print sum}' sales.csv")
T("Field and delimiter", "text", "6.2",
  "A field is one column of a line; the delimiter is the character that separates columns (space, comma, tab, colon).",
  "<code>cut -d: -f1 /etc/passwd</code> uses <code>:</code> as the delimiter and takes field 1. <code>cut</code> uses one exact character; awk's default treats any run of spaces as one separator, which suits command output.",
  ex="cut -d: -f1,7 /etc/passwd")
T("sort and uniq", "text", "6.2",
  "<code>sort</code> orders lines; <code>uniq</code> removes repeated lines; <code>uniq -c</code> counts them.",
  "uniq only removes <b>adjacent</b> duplicates, so you almost always <code>sort</code> first. sort can handle files bigger than RAM by sorting chunks into temporary files and merging them. <code>sort -n</code> numeric, <code>-h</code> human sizes, <code>-k</code> by column.",
  ex="cut -d' ' -f1 access.log | sort | uniq -c | sort -nr | head")
T("cut, tr and wc", "text", "6.2",
  "<code>cut</code> takes columns, <code>tr</code> replaces or deletes characters, <code>wc</code> counts lines, words and bytes.",
  "<code>wc -l</code> counts newline characters, so a last line with no newline is not counted. <code>tr</code> works on single characters, not words (<code>tr 'a-z' 'A-Z'</code>).",
  ex="echo 'hello' | tr a-z A-Z; wc -l /etc/passwd")
T("diff", "text", "6.3",
  "Shows the differences between two files, line by line.",
  "It computes the longest common sequence of lines and prints only what must be added or removed to turn one file into the other. <code>diff -u</code> gives the unified format used by patches and git.",
  ex="diff -u old.conf new.conf")
T("jq", "text", "13.5",
  "A command-line tool to read and reshape JSON: <code>curl -s api | jq '.items[].name'</code>.",
  "jq parses the JSON into a tree and runs a filter expression over it. It is the JSON equivalent of awk and is common in cloud and DevOps scripts.",
  ex="echo '{\"city\":\"Pune\"}' | jq -r .city")

# ------------------------------------------------------------------ users
T("User and UID", "users", "8.1",
  "Every account has a name (riya) and a number, the <b>UID</b> (1000). root is UID 0.",
  "The kernel only knows numbers; names are looked up in <code>/etc/passwd</code> for display. Files store the owner's UID, so if a user is deleted, <code>ls -l</code> shows a bare number instead of a name.",
  ex="id")
T("Group and GID", "users", "8.3",
  "A named set of users, used to share access. Each user has one primary group and can be in more (supplementary).",
  "Group membership is read when you log in, so after <code>usermod -aG docker riya</code> she must log out and in again (or run <code>newgrp</code>) before it takes effect.",
  ex="groups; getent group sudo")
T("/etc/passwd", "users", "8.1",
  "The list of user accounts, one per line: <code>riya:x:1000:1000:Riya:/home/riya:/bin/bash</code>.",
  "Seven fields: name, password placeholder (<code>x</code>), UID, GID, comment, home, login shell. Everyone can read it because many programs need names; the password hashes moved to <code>/etc/shadow</code>.",
  ex="getent passwd riya")
T("/etc/shadow", "users", "8.1",
  "Where password hashes are stored. Readable only by root.",
  "It stores a salted one-way hash, not the password (on recent Ubuntu/Debian the hash starts with <code>$y$</code> = yescrypt; older systems use <code>$6$</code> = SHA-512). At login, the typed password is hashed the same way and compared. It also stores password expiry dates used by <code>chage</code>.",
  ex="sudo grep riya /etc/shadow")
T("root (superuser)", "users", "8.4",
  "The all-powerful admin account, UID 0.",
  "The kernel skips most permission checks for a process with effective UID 0. That is why a mistake as root (like <code>rm -rf</code> in the wrong folder) is so dangerous, and why admins work as normal users and use <code>sudo</code> only when needed.")
T("sudo", "users", "8.4",
  "Runs one command as root (or another user): <code>sudo apt update</code>. Asks for <b>your</b> password.",
  "<code>sudo</code> is a SUID-root program, so it starts with root power, checks <code>/etc/sudoers</code> to see whether you are allowed, logs the command, and then runs it as root. It remembers your password for a few minutes.",
  flow="sudo apt update → sudo starts as root (SUID) → checks /etc/sudoers → asks your password → logs it → runs apt as UID 0",
  ex="sudo -l")
T("su", "users", "8.4",
  "Switches to another user's shell: <code>su - riya</code>. Asks for <b>that user's</b> password.",
  "<code>su -</code> starts a full login shell (their environment and home); plain <code>su</code> keeps much of yours. Many systems lock root's password, so <code>sudo -i</code> is used instead of <code>su -</code>.")
T("sudoers and visudo", "users", "8.4",
  "<code>/etc/sudoers</code> lists who may use sudo for what. Always edit it with <code>visudo</code>.",
  "<code>visudo</code> checks the syntax before saving, because one typo in sudoers can lock everyone out of sudo. Drop-in files go in <code>/etc/sudoers.d/</code>. On Ubuntu, members of group <code>sudo</code> may use it; on RHEL, group <code>wheel</code>.",
  ex="sudo visudo")
T("Real vs effective UID", "users", "9.4",
  "The real UID is who started a process; the effective UID is whose permissions it uses right now.",
  "They are normally the same. A SUID program (like <code>passwd</code>) runs with the file owner's effective UID (root) while the real UID stays yours, so it knows whose password to change.")

# ------------------------------------------------------------------ perms
T("Permission bits (rwx)", "perms", "9.1",
  "Three sets of read, write, execute: for the owner, the group and others. <code>-rw-r--r--</code>.",
  "On every open, the kernel picks <b>one</b> class: owner if your UID matches, else group if you are in the file's group, else others, and checks only that class's bits. So if the owner has fewer rights than the group, the owner still gets the owner's bits.",
  flow="open('report.txt') → UID = owner? use owner bits → else in group? use group bits → else others → allow or 'Permission denied'",
  ex="ls -l report.txt")
T("Permissions on directories", "perms", "9.1",
  "On a folder, <code>r</code> = list names, <code>w</code> = create, delete or rename files inside, <code>x</code> = enter it and reach files inside.",
  "Deleting a file needs <code>w</code> on the <b>folder</b>, not on the file. Without <code>x</code> on a folder you cannot open anything inside even if the file itself is readable.",
  ex="ls -ld ~")
T("Octal (numeric) mode: 755, 644", "perms", "9.2",
  "Permissions written as numbers: r = 4, w = 2, x = 1, added per class. 755 = rwxr-xr-x, 644 = rw-r--r--, 600 = rw-------.",
  "Each digit is three bits, exactly how the kernel stores them in the inode. An optional fourth leading digit holds SUID (4), SGID (2) and sticky (1), e.g. 1777 for /tmp.",
  ex="chmod 600 ~/.ssh/id_ed25519")
T("chmod", "perms", "9.2",
  "Changes permissions: <code>chmod +x deploy.sh</code>, <code>chmod 640 app.conf</code>, <code>chmod -R g+w shared/</code>.",
  "Only the owner (or root) can change a file's mode. It updates the mode bits in the inode; the file's data is not touched, so it is instant even for huge files.")
T("chown and chgrp", "perms", "9.3",
  "Change the owner and group of a file: <code>sudo chown www-data:www-data /var/www/site -R</code>.",
  "Only root can give a file to another user (otherwise users could dodge disk quotas). A normal owner may change the group to one they belong to.")
T("umask", "perms", "9.3",
  "Decides the default permissions of new files and folders. Common value 022 → files 644, folders 755.",
  "Programs ask for 666 (files) or 777 (folders) and the kernel removes the umask bits: 666 − 022 = 644. It is inherited by child processes and set in startup files.",
  ex="umask; touch x; ls -l x")
T("SUID", "perms", "9.4",
  "A special bit on a program: it runs with the permissions of the file's owner, not the user who started it.",
  "<code>/usr/bin/passwd</code> is owned by root with SUID (<code>-rwsr-xr-x</code>), so it can update <code>/etc/shadow</code> for you. Linux ignores SUID on scripts for safety. Unexpected SUID files are a classic security finding.",
  ex="ls -l /usr/bin/passwd; find / -perm -4000 2>/dev/null")
T("SGID", "perms", "9.4",
  "On a program: runs with the file's group. On a folder: new files inside get the folder's group.",
  "SGID on a shared project folder (<code>chmod g+s /srv/team</code>) means everyone's new files belong to the team group automatically.",
  ex="chmod g+s /srv/team")
T("Sticky bit", "perms", "9.4",
  "On a shared folder: users can delete or rename only their own files.",
  "Shown as <code>t</code> in the others' execute position (<code>drwxrwxrwt</code> on /tmp). The kernel adds an extra check on unlink and rename in that folder: you must own the file or the folder (or be root).",
  ex="ls -ld /tmp")
T("ACL (access control list)", "perms", "9.5",
  "Extra permission rules for specific users or groups, beyond owner/group/others.",
  "Stored as extended attributes on the file. <code>ls -l</code> shows a <code>+</code> after the mode when ACLs exist. A <b>mask</b> entry limits the maximum rights any ACL entry can give.",
  ex="setfacl -m u:meera:r report.csv; getfacl report.csv")
T("Immutable attribute (chattr +i)", "perms", "9.5",
  "A file flag that stops <b>anyone</b>, even root, from changing, renaming or deleting the file until the flag is removed.",
  "It is stored by the file system (ext4, xfs) and checked by the kernel before any change. Useful to protect critical configs; confusing if you forget it is set (\"Operation not permitted\" as root).",
  ex="sudo chattr +i /etc/resolv.conf; lsattr /etc/resolv.conf")

# ------------------------------------------------------------------ proc
T("Process", "proc", "11.1",
  "A running program. One program file can run as many processes.",
  "The kernel gives each process its own memory, open files, current folder, user ID and a <b>PID</b>, and switches the CPU between them many times a second.",
  ex="ps -ef | head")
T("PID and PPID", "proc", "11.1",
  "PID = the process's ID number. PPID = the ID of the process that started it (its parent).",
  "All processes form a tree with systemd (PID 1) at the top. <code>$$</code> is your shell's PID.",
  ex="echo $$; ps -o pid,ppid,comm; pstree -p | head")
T("fork and exec", "proc", "11.1",
  "How every new program starts: the shell <b>forks</b> (copies itself) and the copy <b>execs</b> (turns into) the new program.",
  "<code>fork()</code> creates a child that shares memory pages copy-on-write, so it is fast. <code>execve()</code> then replaces the child's memory with the new program but keeps its open file descriptors, which is how redirections set up before exec survive.",
  flow="bash (PID 500) → fork → child bash (PID 501) → set up redirections → execve('/usr/bin/ls') → PID 501 is now ls → exits → bash wait()s",
  ex="strace -f -e trace=execve bash -c 'ls >/dev/null'")
T("Process states", "proc", "11.2",
  "The STAT column in <code>ps</code>: R running, S sleeping, D waiting for disk/IO, T stopped, Z zombie.",
  "Most processes sleep (S) waiting for input. Many processes stuck in <b>D</b> usually means slow or hung storage (for example an NFS mount), and they push up the load average.",
  ex="ps -eo pid,stat,comm | head")
T("Zombie process", "proc", "11.1",
  "A process that has finished but whose parent has not yet collected its exit status. Shows as <code>Z</code> / &lt;defunct&gt;.",
  "It uses no CPU or memory, only a process-table entry. You cannot kill it (it is already dead); the parent must call <code>wait()</code>, or be killed so PID 1 adopts and reaps it.",
  ex="ps -eo pid,ppid,stat,comm | awk '$3 ~ /Z/'")
T("Orphan process", "proc", "11.1",
  "A process whose parent has exited. It keeps running.",
  "The kernel re-parents it to PID 1 (or a designated \"subreaper\"), which will collect its exit status when it finishes.")
T("Daemon", "proc", "11.1",
  "A background program with no terminal that provides a service. Names often end in d: sshd, crond, systemd-journald.",
  "Modern daemons are started and supervised by systemd, which restarts them if they crash and captures their output into the journal.",
  ex="systemctl list-units --type=service --state=running")
T("Thread", "proc", "11.2",
  "A separate line of execution inside a process. Threads share the process's memory.",
  "The Linux kernel schedules each thread as its own task with a thread ID; <code>ps -L</code> and <code>top -H</code> show them. A Java server process can have hundreds.",
  ex="ps -eLf | wc -l")
T("Signal", "proc", "11.3",
  "A small message the kernel delivers to a process: stop, continue, terminate, reload.",
  "When a signal arrives, the process runs its handler, uses the default action, or ignores it. SIGKILL and SIGSTOP cannot be caught or ignored. <code>kill</code> does not only kill: it sends any signal.",
  flow="kill -TERM 4321 → kill() system call → kernel marks signal pending → process runs its handler / default → exits cleanly",
  ex="kill -l")
T("SIGTERM vs SIGKILL (kill vs kill -9)", "proc", "11.3",
  "SIGTERM (15, the default) politely asks a program to stop. SIGKILL (9) makes the kernel end it immediately.",
  "SIGTERM can be handled: the app can save data, close connections and delete temp files. SIGKILL gives no chance to clean up, which can leave lock files or half-written data. Try TERM first, wait, then KILL.",
  ex="kill 4321; sleep 5; kill -9 4321")
T("SIGINT and SIGHUP", "proc", "11.3",
  "SIGINT (2) is sent by <kbd>Ctrl</kbd>+<kbd>C</kbd>. SIGHUP (1) is sent when the terminal closes; many daemons treat it as \"reload your config\".",
  "Your terminal driver turns <kbd>Ctrl</kbd>+<kbd>C</kbd> into SIGINT for the foreground job. A command killed this way ends with exit status 130 (128 + 2).",
  ex="sudo kill -HUP $(pidof nginx)")
T("trap", "proc", "11.3",
  "A shell command to run your own code when a signal arrives or the script exits: <code>trap 'rm -f /tmp/lock' EXIT</code>.",
  "bash installs a handler with the kernel; when the signal is delivered, it runs your command. Used for cleanup in scripts.",
  ex="trap 'echo bye' EXIT")
T("nohup", "proc", "11.4",
  "Runs a command that keeps going after you log out: <code>nohup ./train.sh &</code>.",
  "It sets the process to ignore SIGHUP and, if output is a terminal, sends it to <code>nohup.out</code>. For anything long-running on a server, a systemd service or tmux is more reliable.",
  ex="nohup python3 job.py > job.log 2>&1 &")
T("nice value and priority", "proc", "11.5",
  "A number from −20 (greedy) to 19 (very polite) that changes how much CPU a process gets when the CPU is busy.",
  "The scheduler gives each task a share of CPU weighted by its nice value. Normal users can only make their processes nicer (raise the number); lowering it needs root.",
  ex="nice -n 10 tar czf backup.tgz /data; renice 5 -p 4321")
T("Load average", "proc", "18.3",
  "Three numbers from <code>uptime</code> (1, 5 and 15 minutes): how many tasks were running or waiting.",
  "On Linux it counts tasks that are runnable <b>and</b> tasks in uninterruptible sleep (D, usually disk I/O). Compare it with your number of CPUs (<code>nproc</code>): 4.0 on a 4-CPU machine is busy but fine; 20 means work is queuing.",
  ex="uptime; nproc")
T("Context switch", "proc", "18.3",
  "When the CPU stops running one task and starts another.",
  "The kernel saves the registers of one task and loads the next. Thousands per second is normal; a huge number (seen in <code>vmstat</code>'s <code>cs</code> column) can mean too many threads fighting.",
  ex="vmstat 1 5")

# ------------------------------------------------------------------ services
T("Service / unit (systemd)", "services", "17.2",
  "A background program managed by systemd, described by a unit file such as <code>nginx.service</code>.",
  "Unit files live in <code>/usr/lib/systemd/system</code> (from packages) and <code>/etc/systemd/system</code> (yours, which win). They say what to run, as which user, what it depends on and whether to restart it.",
  ex="systemctl cat ssh")
T("systemctl start vs enable", "services", "17.2",
  "<code>start</code> runs a service now. <code>enable</code> makes it start at every boot. They are independent.",
  "<code>enable</code> just creates a symlink in a target's <code>.wants</code> folder (for example <code>multi-user.target.wants</code>); nothing starts until the next boot. <code>enable --now</code> does both.",
  ex="sudo systemctl enable --now nginx")
T("Target", "services", "17.5",
  "A group of units that defines a system state, like <code>multi-user.target</code> (server, no GUI) or <code>graphical.target</code>.",
  "Targets replace the old SysV runlevels (3 ≈ multi-user, 5 ≈ graphical). Booting means systemd pulling in the default target and everything it wants.",
  ex="systemctl get-default")
T("systemd timer", "services", "17.3",
  "A systemd alternative to cron: runs a service on a schedule.",
  "A <code>.timer</code> unit triggers a matching <code>.service</code>. Advantages over cron: logs go to the journal, it can catch up missed runs (<code>Persistent=true</code>), and dependencies are respected.",
  ex="systemctl list-timers")
T("cron and crontab", "services", "17.4",
  "cron runs commands on a schedule. Each user's schedule is their crontab: <code>30 2 * * * /opt/backup.sh</code> = every day at 02:30.",
  "The cron daemon wakes every minute and checks all crontabs. Jobs run with a very small environment (short PATH, no aliases, your <code>.bashrc</code> not loaded), which is the number-one reason a script works by hand but fails in cron. Use full paths and log the output.",
  flow="minute ticks → crond reads crontabs → time matches '30 2 * * *' → runs /bin/sh -c '/opt/backup.sh' with minimal env → output mailed or lost unless redirected",
  ex="crontab -l; crontab -e")
T("Journal (journald, journalctl)", "services", "18.1",
  "systemd's central log of all services and the kernel. Read it with <code>journalctl</code>.",
  "journald collects stdout/stderr of every service, syslog messages and kernel messages, stores them in binary indexed files (in <code>/var/log/journal</code> when persistent), and can filter by unit, time and priority quickly.",
  ex="journalctl -u nginx --since '1 hour ago'; journalctl -p err -b")
T("/var/log and syslog", "services", "18.1",
  "The folder of text log files: <code>syslog</code> or <code>messages</code>, <code>auth.log</code> or <code>secure</code>, app logs.",
  "rsyslog receives messages (often forwarded from journald) and writes them to files according to rules in <code>/etc/rsyslog.conf</code>. Names differ: Ubuntu uses <code>auth.log</code>, RHEL uses <code>secure</code>.",
  ex="sudo tail -f /var/log/auth.log")
T("dmesg (kernel ring buffer)", "services", "18.1",
  "Messages from the kernel itself: hardware, drivers, disk errors, the OOM killer.",
  "The kernel writes to a fixed-size in-memory ring buffer; old messages are overwritten. <code>dmesg -T</code> shows readable times; <code>journalctl -k</code> shows the same messages from the journal.",
  ex="sudo dmesg -T | tail")
T("logrotate", "services", "18.2",
  "Keeps logs from filling the disk by renaming, compressing and deleting old ones on a schedule.",
  "Typical cycle: <code>app.log</code> → <code>app.log.1</code> → <code>app.log.2.gz</code> …, then a new empty <code>app.log</code>, and a <code>postrotate</code> command tells the app to reopen its file. <code>copytruncate</code> is used for apps that cannot reopen.",
  ex="cat /etc/logrotate.d/rsyslog")

# ------------------------------------------------------------------ pkg
T("Package (.deb, .rpm)", "pkg", "14.1",
  "A ready-to-install bundle of a program's files plus information: name, version, dependencies and install scripts.",
  "Installing a package copies its files into place, runs its scripts and records every file in the package database, so it can later be upgraded or removed cleanly.",
  ex="dpkg -L coreutils | head")
T("Repository", "pkg", "14.1",
  "An online store of packages for your distro, with a signed index.",
  "<code>apt update</code> downloads only the index (package lists, into <code>/var/lib/apt/lists</code>). <code>apt install</code> then works out dependencies, downloads <code>.deb</code> files, checks their signatures and calls <code>dpkg</code> to install them.",
  flow="apt update → download signed index → apt install nginx → resolve dependencies → download .debs → verify signatures → dpkg unpacks + runs scripts → service starts",
  ex="apt policy nginx")
T("apt vs dpkg", "pkg", "14.2",
  "<code>dpkg</code> installs a single .deb file and does not fetch dependencies. <code>apt</code> fetches from repositories and handles dependencies, then uses dpkg.",
  "Same pattern on RHEL: <code>rpm</code> is the low-level tool, <code>dnf</code> (formerly <code>yum</code>) the high-level one. <code>apt</code> is the friendly command; <code>apt-get</code> is the older one with output that is stable for scripts.",
  ex="sudo apt install ./app.deb")
T("dnf / yum and rpm", "pkg", "14.3",
  "The package tools of Fedora, RHEL, Rocky and AlmaLinux.",
  "<code>dnf</code> reads repo files in <code>/etc/yum.repos.d/</code>, resolves dependencies and calls rpm. On current RHEL, the <code>yum</code> command is kept as a link to dnf.",
  ex="sudo dnf install httpd; rpm -qa | head")
T("Dependency", "pkg", "14.1",
  "Another package that a package needs in order to work (a library, a runtime).",
  "Package metadata lists dependencies with version rules. The package manager installs them automatically, and <code>apt autoremove</code> removes ones nothing needs any more.")
T("Shared library (.so)", "pkg", "14.4",
  "Code that many programs use at run time, like <code>libc.so.6</code>. The Linux version of a Windows DLL.",
  "When a program starts, the dynamic loader (<code>ld-linux</code>) finds and maps the libraries it needs. \"error while loading shared libraries\" means one is missing.",
  ex="ldd /usr/bin/ls")
T("snap and Flatpak", "pkg", "14.4",
  "Package formats that bundle an app with its own libraries and run it in a sandbox, the same on any distro.",
  "Each snap is a compressed squashfs image mounted read-only (you will see <code>/dev/loop</code> devices in <code>lsblk</code>). Bigger downloads, but no dependency conflicts and automatic updates.",
  ex="snap list")
T("Building from source", "pkg", "14.4",
  "Compiling a program yourself from its code: usually <code>./configure && make && sudo make install</code>.",
  "<code>configure</code> checks your system and writes a Makefile; <code>make</code> compiles; <code>make install</code> copies files, by default under <code>/usr/local</code> so they do not clash with packages. The package manager does not know about these files.")
T("tar archive", "pkg", "14.5",
  "Bundles many files and folders into one file (<code>.tar</code>), keeping permissions and structure.",
  "tar itself does not compress; it is usually combined with gzip (<code>.tar.gz</code>/<code>.tgz</code>), bzip2 or xz. <code>c</code> create, <code>x</code> extract, <code>t</code> list, <code>z</code> gzip, <code>f</code> file name.",
  ex="tar czf site.tgz /var/www/site; tar tzf site.tgz | head")
T("Compression (gzip, bzip2, xz, zip)", "pkg", "14.5",
  "Makes files smaller. gzip is fast and common; xz squeezes most but is slowest; zip is for sharing with Windows.",
  "Text logs often shrink by 90% or more because they repeat a lot. <code>zcat</code>, <code>zgrep</code> and <code>zless</code> read .gz files without extracting them.",
  ex="gzip big.log; zgrep ERROR big.log.gz")

# ------------------------------------------------------------------ net
T("Network interface", "net", "16.2",
  "A network connection point of the machine: <code>lo</code>, <code>eth0</code>/<code>ens33</code>/<code>enp0s3</code> (wired), <code>wlan0</code> (Wi-Fi).",
  "Names like <code>enp0s3</code> are \"predictable names\" built from the hardware location, so they do not change between boots like eth0/eth1 used to.",
  ex="ip -br addr")
T("IP address and CIDR (/24)", "net", "16.1",
  "The address of a machine on a network, like <code>192.168.1.20/24</code>. <code>/24</code> means the first 24 bits are the network part.",
  "With /24, addresses 192.168.1.0–255 are on the same local network and talk directly; anything else goes through the default gateway.",
  ex="ip addr show")
T("Loopback (127.0.0.1, localhost)", "net", "16.1",
  "An address that always means \"this same machine\".",
  "Traffic to 127.0.0.1 goes through the <code>lo</code> interface and never leaves the computer. A service listening only on 127.0.0.1 cannot be reached from other machines, a common \"works on the server but not from my laptop\" cause.")
T("Default gateway and routes", "net", "16.2",
  "The router your machine sends traffic to when the destination is not on the local network.",
  "The kernel's routing table picks the most specific matching route for each packet; <code>default via 192.168.1.1</code> catches everything else.",
  ex="ip route")
T("Port", "net", "16.1",
  "A number (0–65535) that picks which service on a machine receives the traffic: 22 SSH, 80 HTTP, 443 HTTPS, 3306 MySQL.",
  "An IP address finds the machine; the port finds the program. Ports below 1024 normally need root (or the CAP_NET_BIND_SERVICE capability) to listen on.",
  ex="grep -w 22 /etc/services")
T("Socket and listening", "net", "16.4",
  "A socket is a network connection endpoint. A server <b>listens</b> on a port and accepts connections.",
  "To a program, a socket is just another file descriptor it reads and writes. <code>ss -tlnp</code> shows TCP sockets in LISTEN state and which process owns them; \"Address already in use\" means one is already listening.",
  ex="sudo ss -tlnp")
T("TCP vs UDP", "net", "16.1",
  "TCP is reliable and ordered (web, SSH, databases). UDP is fast with no guarantees (DNS queries, video calls, games).",
  "TCP sets up a connection with a three-way handshake and resends lost data; UDP just sends packets.")
T("DNS and name resolution", "net", "16.3",
  "DNS turns names like <code>myphatshala.in</code> into IP addresses.",
  "Most programs ask the C library, which follows <code>/etc/nsswitch.conf</code> (<code>hosts: files dns</code>): first <code>/etc/hosts</code>, then the DNS server in <code>/etc/resolv.conf</code> (on Ubuntu, the local systemd-resolved stub 127.0.0.53). <code>dig</code> and <code>nslookup</code> query DNS directly and skip <code>/etc/hosts</code>, so they can disagree with what <code>ping</code> uses.",
  flow="curl myphatshala.in → libc → nsswitch: files → /etc/hosts? no → dns → resolver in resolv.conf → answer IP → connect",
  ex="getent hosts myphatshala.in; dig +short myphatshala.in")
T("/etc/hosts", "net", "16.2",
  "A local text file mapping names to IP addresses, checked before DNS.",
  "Useful to test a new server before DNS changes or to name lab machines (e.g. Hadoop nodes). A forgotten entry here explains \"why does only my machine reach the old server?\"",
  ex="cat /etc/hosts")
T("ping (ICMP)", "net", "16.3",
  "Checks if a machine is reachable and how long a round trip takes.",
  "It sends ICMP echo requests and times the replies. Many cloud servers and firewalls block ICMP, so no reply does not prove the machine is down; test the real port with <code>nc -zv host 443</code> or <code>curl</code>.",
  ex="ping -c 4 8.8.8.8")
T("traceroute", "net", "16.3",
  "Shows each router hop on the way to a destination.",
  "It sends packets with TTL = 1, 2, 3…; each router that drops a packet when TTL reaches 0 sends back an error, revealing itself. <code>mtr</code> does this continuously.",
  ex="traceroute google.com")
T("SSH", "net", "16.6",
  "Secure Shell: log in to and run commands on a remote Linux machine over an encrypted connection.",
  "Client and server agree on encryption keys; the client checks the server's host key against <code>~/.ssh/known_hosts</code> (warning if it changed); then you log in by password or, better, by key.",
  flow="ssh riya@server → TCP to port 22 → key exchange (encrypted channel) → server host key checked in known_hosts → user auth (key/password) → remote shell",
  ex="ssh -v riya@192.168.1.20")
T("SSH key pair", "net", "16.6",
  "Two linked files: a <b>private key</b> that stays on your laptop and a <b>public key</b> you put on servers.",
  "The server stores your public key in <code>~/.ssh/authorized_keys</code>. At login it sends a challenge; your client signs it with the private key; the server checks the signature with the public key. The private key never leaves your machine, so nothing reusable crosses the network.",
  ex="ssh-keygen -t ed25519; ssh-copy-id riya@server")
T("scp vs rsync", "net", "16.6",
  "Both copy files over SSH. <code>scp</code> always copies everything; <code>rsync</code> sends only what changed.",
  "rsync compares files (size and time, or checksums) and, for changed files, sends only the differing blocks using a rolling checksum. Re-running a big backup moves almost nothing. <code>rsync -avz --delete src/ dest/</code> (the trailing slash matters).",
  ex="rsync -avz ./site/ riya@server:/var/www/site/")
T("curl and wget", "net", "16.5",
  "Command-line tools to fetch URLs. <code>wget</code> is mainly for downloading files; <code>curl</code> for any HTTP request, including APIs.",
  "<code>curl -I</code> shows only headers, <code>-v</code> shows the whole conversation (DNS, TLS, request, response), <code>-X POST -d</code> sends data. Very handy to test a web service from the server itself.",
  ex="curl -I https://myphatshala.in")
T("Firewall (netfilter: iptables, nftables, ufw, firewalld)", "net", "19.1",
  "Rules in the kernel that allow or block network traffic by port, address and protocol.",
  "The filtering is done by <b>netfilter</b> inside the kernel. <code>nftables</code> (and the older <code>iptables</code>) write rules into it; <code>ufw</code> (Ubuntu) and <code>firewalld</code> (RHEL) are simpler front ends that generate those rules.",
  flow="packet arrives → kernel netfilter hooks → rules checked top-down → ACCEPT → delivered to the listening socket (or DROP)",
  ex="sudo ufw allow 22/tcp; sudo ufw status")

# ------------------------------------------------------------------ sec
T("User space vs kernel space", "sec", "20.1",
  "Two areas of the computer: programs run in user space; the kernel runs in protected kernel space.",
  "The CPU enforces the boundary. A crashing program only kills itself; a crashing kernel (a \"kernel panic\") stops the whole machine.")
T("System call", "sec", "20.1",
  "The only way a program can ask the kernel for something: open a file, read, write, start a process, open a network connection.",
  "There are a few hundred (open, read, write, fork, execve, socket…). <code>strace</code> shows every call a program makes and is a powerful debugging tool: \"which config file is it actually reading?\"",
  ex="strace -c ls >/dev/null; strace -e trace=openat cat /etc/hostname")
T("Kernel module", "sec", "20.1",
  "A piece of the kernel (usually a driver) loaded or removed while the system runs: a <code>.ko</code> file.",
  "udev loads the right module when hardware appears; <code>modprobe</code> loads one with its dependencies. Modules live in <code>/lib/modules/$(uname -r)</code>.",
  ex="lsmod | head; modinfo ext4")
T("Capabilities", "sec", "20.3",
  "Root's powers split into separate pieces, e.g. CAP_NET_BIND_SERVICE (use ports below 1024).",
  "A program can be given just the piece it needs instead of full root, reducing damage if it is hacked. Containers drop most capabilities by default.",
  ex="getcap /usr/bin/ping")
T("SELinux", "sec", "19.2",
  "An extra security layer (default on RHEL, Fedora, Rocky) that limits what each program may touch, even when running as root.",
  "Every process and file has a label; the kernel checks policy rules on each access, after normal permissions. Typical surprise: the files look fine with <code>ls -l</code>, but Apache gets \"Permission denied\" because of a wrong label. Check <code>getenforce</code> and the audit log before disabling it.",
  ex="getenforce; ls -Z /var/www/html")
T("AppArmor", "sec", "19.2",
  "Ubuntu's and Debian's equivalent of SELinux: per-program profiles saying which paths it may use.",
  "Profiles in <code>/etc/apparmor.d/</code> work by file path instead of labels, so they are simpler to read and write.",
  ex="sudo aa-status")
T("fail2ban", "sec", "19.3",
  "A service that blocks IP addresses after too many failed logins.",
  "It watches logs (for example <code>auth.log</code> for SSH), counts failures per IP, and adds a firewall rule to ban the IP for a while. Internet-facing servers see automated SSH login attempts every day.",
  ex="sudo fail2ban-client status sshd")
T("Checksum / hash (sha256sum)", "sec", "19.4",
  "A short fingerprint of a file. If even one byte changes, the fingerprint changes completely.",
  "Download sites publish the SHA-256 of an ISO; you compute it yourself and compare. A <b>GPG signature</b> goes further: it proves who published the checksum.",
  ex="sha256sum ubuntu.iso; sha256sum -c SHA256SUMS")
T("Namespace", "sec", "20.3",
  "A kernel feature that gives a group of processes its own private view of something: process IDs, mounts, network, hostname, users.",
  "Inside a new PID namespace the first process sees itself as PID 1; inside a network namespace it has its own interfaces and ports. Containers are built from these. <code>unshare</code> and <code>nsenter</code> create and enter them.",
  ex="lsns | head")
T("cgroup (control group)", "sec", "20.3",
  "A kernel feature that groups processes and limits or measures their CPU, memory and disk I/O.",
  "systemd puts every service in its own cgroup (that is how it can stop all of a service's child processes). Docker's <code>--memory=512m</code> is a cgroup limit; exceeding it triggers the OOM killer inside that group only. cgroup v2 is mounted at <code>/sys/fs/cgroup</code>.",
  ex="systemd-cgls | head; cat /proc/self/cgroup")
T("Container", "sec", "20.3",
  "An app packaged with its files, running isolated on a shared Linux kernel (Docker, Podman, Kubernetes pods).",
  "A container is <b>not</b> a VM: it is ordinary Linux processes, isolated with namespaces, limited with cgroups, with a layered image file system (overlayfs) as its root. That is why it starts in milliseconds, and why Linux knowledge is essential for DevOps.",
  flow="docker run → image layers mounted (overlayfs) → new namespaces (pid, net, mnt…) → cgroup limits set → your process starts as PID 1 inside")

# ------------------------------------------------------------------ added 5 Nov 2026 (kernel architecture review + Module 2)
T("Interrupt", "sec", "1.2",
  "A signal from hardware (key press, network packet, disk done, timer) that makes the CPU pause and run kernel code.",
  "The CPU saves what it was doing and jumps to a short kernel <b>interrupt handler</b>, which runs in interrupt context (it must not sleep). The handler usually just records the event and wakes a waiting process, then the CPU resumes. Counts per device are in <code>/proc/interrupts</code>.",
  flow="key press → keyboard controller raises IRQ → CPU pauses current task → kernel handler reads key → wakes bash → CPU resumes",
  ex="head -5 /proc/interrupts", aka="IRQ")
T("Process scheduler", "proc", "1.2",
  "The kernel part that decides which task runs on which CPU core next, and for how long.",
  "Runnable tasks wait in per-CPU queues; the scheduler picks by fairness and priority (nice). Since Linux 6.6 the default algorithm is EEVDF, which replaced CFS. Every switch is a context switch; the total is the <code>ctxt</code> line of <code>/proc/stat</code>.",
  ex="grep ctxt /proc/stat", aka="EEVDF, CFS")
T("Virtual file system (VFS)", "fs", "1.2",
  "The kernel layer that gives every program one way (open, read, write) to use any file system: ext4, xfs, FAT, network shares.",
  "A system call such as <code>openat</code> enters the VFS, which looks the path up in its caches (dentries, inodes) and calls the right file-system driver. That is why <code>cat</code> works the same on your SSD and on a USB stick.",
  flow="cat file → openat() → VFS → ext4 / xfs / vfat driver → block layer → disk",
  ex="grep -v nodev /proc/filesystems")
T("MMU (memory management unit)", "storage", "1.2",
  "The part of the CPU that translates the virtual addresses programs use into real RAM addresses.",
  "The kernel writes page tables; the MMU reads them on every memory access and raises a fault if a program touches memory it does not own (a segmentation fault) or a page is not in RAM yet (a page fault the kernel then fixes).")
T("Protection rings (ring 0 / ring 3)", "sec", "1.2",
  "CPU privilege levels: the kernel runs in ring 0 with full power; programs run in ring 3 with limited power.",
  "A system call is the controlled jump from ring 3 to ring 0 and back. ARM CPUs use exception levels (EL0 for programs, EL1 for the kernel) for the same idea.")
T("LSM (Linux Security Modules)", "sec", "19.2",
  "The kernel framework that lets security systems such as SELinux and AppArmor add extra rules on every access.",
  "Before sensitive operations (open a file, bind a port) the kernel calls LSM hooks; the active module answers allow or deny, after normal permissions have been checked. The code lives in the <code>security/</code> folder of the kernel source.")
T("Merge window", "basics", "1.2",
  "The two weeks after each kernel release when new features are accepted for the next version.",
  "Subsystem maintainers send pull requests to Linus Torvalds; after the window, only fixes go in through weekly release candidates (-rc1, -rc2 …). A new kernel appears roughly every nine to ten weeks.")
T("Kernel source tree", "sec", "1.2",
  "How the Linux kernel’s code is organised into folders: arch, drivers, fs, mm, net, kernel, ipc, block, security.",
  "Each folder is a subsystem with its own maintainers: <code>kernel/sched/</code> the scheduler, <code>mm/</code> memory, <code>fs/</code> file systems, <code>net/</code> networking, <code>drivers/</code> hardware (the biggest part), <code>arch/</code> CPU-specific code.")
T("/boot", "fs", "2.1",
  "The folder with the kernel image and the files the boot loader needs: <code>vmlinuz-…</code>, <code>initrd.img-…</code>, GRUB settings.",
  "GRUB reads these files before Linux is running. A full <code>/boot</code> (too many old kernels) can make kernel updates fail, a classic server problem.",
  ex="ls /boot")
T("/opt", "fs", "2.1",
  "Optional, add-on software installed outside the package manager, usually by vendors: <code>/opt/google/chrome</code>, <code>/opt/app</code>.",
  "Each product gets its own subfolder, so it can be removed by deleting one folder. Package-managed software goes to <code>/usr</code> instead.")
T("/mnt and /media", "fs", "2.1",
  "Mount points: <code>/media</code> for removable media mounted automatically (USB sticks), <code>/mnt</code> for things an admin mounts by hand.",
  "They are ordinary empty folders until a file system is mounted on them (Lesson 15.3). On WSL, Windows drives appear under <code>/mnt/c</code>.",
  ex="ls /mnt")
T("/lib", "fs", "2.1",
  "Shared libraries and kernel modules needed by programs in /bin and /sbin: <code>libc.so.6</code>, <code>/lib/modules/&lt;version&gt;</code>.",
  "On merged-/usr systems <code>/lib</code> is a link to <code>/usr/lib</code>. The dynamic loader finds libraries here when a program starts.",
  ex="readlink -f /lib")
T("lost+found", "fs", "2.1",
  "A folder at the top of every ext4 file system where <code>fsck</code> puts recovered pieces of damaged files.",
  "It is normally empty and owned by root. If you see files in it, the file system was repaired after a crash.")
T("Unix epoch and timestamps", "fs", "2.4",
  "Linux stores times as seconds since 1 January 1970 (UTC), the Unix epoch. Each file has access, modify and change times.",
  "<b>mtime</b> = content last modified, <b>ctime</b> = inode (permissions, owner, name) last changed, <b>atime</b> = last read (often updated lazily). <code>stat</code> shows all three; <code>date +%s</code> prints the current epoch seconds.",
  ex="date +%s; stat -c '%y' /etc/hostname", aka="mtime, ctime, atime")
T("apropos and whatis", "shell", "2.5",
  "<code>whatis ls</code> prints the one-line description of a command; <code>apropos copy</code> (= <code>man -k</code>) searches all descriptions for a word.",
  "Both search a small database built from the man pages (updated by <code>mandb</code>), so they are instant.",
  ex="apropos -s1 copy | head -3")
T("info pages", "shell", "2.5",
  "GNU’s longer, hyperlinked manuals: <code>info coreutils</code>. Often more detailed than the man page.",
  "Navigate with arrows, Enter to follow a link, <kbd>q</kbd> to quit. Many GNU man pages end with “the full documentation is maintained as a Texinfo manual”.")
T("ls -l columns", "fs", "2.2",
  "In <code>-rw-r--r-- 1 riya riya 120 Nov 5 10:05 notes.txt</code>: type+permissions, link count, owner, group, size in bytes, modification time, name.",
  "ls reads all of this from the file’s inode with a <code>statx</code> system call; only the name comes from the directory entry.",
  ex="ls -l /etc/hostname")

# ------------------------------------------------------------------ often confused
CONFUSED = [
 ("Linux vs a distribution", "<b>Linux</b> is the kernel. A <b>distribution</b> (Ubuntu, RHEL) is a full OS built around it: tools, package manager, installer, defaults."),
 ("Terminal vs shell", "The <b>terminal</b> is the window that shows text. The <b>shell</b> (bash) is the program inside it that understands commands. You can change one without the other."),
 ("Absolute vs relative path", "<b>Absolute</b> starts with <code>/</code> and works from anywhere. <b>Relative</b> is from your current folder, so the same command can mean different files in different folders."),
 ("> vs >>", "<code>></code> empties the file first, then writes. <code>>></code> adds to the end. <code>sort data.txt > data.txt</code> leaves an empty file because the shell truncates it before sort reads it."),
 ("Pipe ( | ) vs redirection ( > )", "A <b>pipe</b> sends output to another <i>command</i>. <b>Redirection</b> sends it to a <i>file</i>. <code>ls > grep</code> creates a file named grep."),
 ("Hard link vs soft link", "A <b>hard link</b> is a second name for the same inode; survives deleting the original; same file system only. A <b>soft link</b> is a pointer to a path; breaks if the target moves; can cross file systems and point to folders."),
 ("rm vs freeing disk space", "<code>rm</code> removes a name. Space comes back only when no other hard link exists <i>and</i> no process still has the file open (<code>lsof +L1</code>)."),
 ("Single vs double quotes", "<code>'$HOME'</code> prints the text $HOME. <code>\"$HOME\"</code> prints /home/riya. Both stop spaces from splitting words."),
 ("Shell variable vs environment variable", "A plain <code>X=1</code> exists only in this shell. <code>export X=1</code> also copies it to programs you start. Children can never change the parent's variables."),
 ("source script vs ./script", "<code>source</code> runs the file in your current shell (its <code>cd</code> and variables stay). <code>./script</code> runs in a child process (changes vanish when it ends)."),
 ("su vs sudo", "<b>su</b> switches to another user (asks <i>their</i> password, gives a whole shell). <b>sudo</b> runs one command as root (asks <i>your</i> password, checks sudoers, logs it)."),
 ("chmod vs chown", "<b>chmod</b> changes <i>what</i> can be done (rwx). <b>chown</b> changes <i>who</i> owns the file. Only root can chown to another user."),
 ("kill vs kill -9", "<code>kill</code> sends SIGTERM: the app can clean up and exit. <code>kill -9</code> sends SIGKILL: the kernel ends it instantly, no cleanup. Use -9 only when TERM fails."),
 ("Process vs thread", "A <b>process</b> has its own memory. <b>Threads</b> are parallel paths inside one process, sharing its memory. The kernel schedules both as tasks."),
 ("Zombie vs orphan", "A <b>zombie</b> is dead but not yet collected by its parent. An <b>orphan</b> is alive but its parent died; PID 1 adopts it."),
 ("systemctl start vs enable", "<b>start</b> = run it now. <b>enable</b> = start it automatically at boot. A service can be enabled but stopped, or running but disabled."),
 ("cron vs systemd timer", "<b>cron</b> is simple and everywhere. A <b>timer</b> logs to the journal, can run missed jobs after downtime and respects dependencies."),
 ("apt vs dpkg (dnf vs rpm)", "<b>dpkg</b>/<b>rpm</b> install one local package file with no dependency fetching. <b>apt</b>/<b>dnf</b> download from repositories and resolve dependencies, then call dpkg/rpm."),
 ("apt update vs apt upgrade", "<b>update</b> only refreshes the list of available packages. <b>upgrade</b> actually installs newer versions. Run update first."),
 ("df vs du", "<b>df</b> asks the file system how full it is. <b>du</b> adds up the files it can see. If df says full but du finds little, a deleted-but-open file or files hidden under a mount point are the usual cause."),
 ("free vs available memory", "<b>free</b> is RAM doing nothing at all. <b>available</b> includes cache the kernel will give back instantly. Low \"free\" is normal; low \"available\" is a real problem."),
 ("find vs locate", "<b>find</b> walks the folders right now: always current, slower. <b>locate</b> searches a database updated about daily: instant, but misses new files until <code>updatedb</code> runs."),
 ("grep vs sed vs awk", "<b>grep</b> finds lines. <b>sed</b> changes text in lines (search and replace). <b>awk</b> works with columns and calculations (sums, counts, reports)."),
 ("scp vs rsync", "<b>scp</b> copies everything every time. <b>rsync</b> copies only differences, can resume, preserve permissions and mirror with <code>--delete</code>. Use rsync for backups and deployments."),
 ("dig vs ping for DNS", "<b>dig</b> asks the DNS server directly. <b>ping</b> (and most programs) resolve through <code>/etc/hosts</code> first. If they disagree, check /etc/hosts."),
 ("Interrupt context vs process context", "<b>Interrupt context</b>: the kernel’s short handler for a hardware event; it must not sleep. <b>Process context</b>: kernel code running for a process, for example inside a system call; it may wait."),
 ("ctime vs mtime", "<b>mtime</b> changes when the file’s content changes. <b>ctime</b> changes when its inode changes: permissions, owner, link count, and also content. ctime is not “creation time”."),
 ("man vs --help vs info", "<b>--help</b>: a quick summary printed by the command itself. <b>man</b>: the full reference page. <b>info</b>: GNU’s longer tutorial-style manual with links."),
 ("Container vs virtual machine", "A <b>VM</b> runs its own full kernel on virtual hardware. A <b>container</b> is isolated processes sharing the host's kernel: lighter and faster to start, but the same kernel for all."),
]

# ------------------------------------------------------------------ build
course = json.load(open(os.path.join(ROOT, "courses/linux/course.json")))
mods = course["modules"]
def lesson(ref):
    m, l = (int(x) for x in ref.split("."))
    mo = mods[m - 1]; le = mo["lessons"][l - 1]
    return f"{mo['slug']}/{le['slug']}", le["title"]

def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def strip(s): return re.sub(r"<[^>]+>", "", s)

TERMS.sort(key=lambda t: t["term"].lower().lstrip("/.~(").lstrip())
counts = {g: sum(1 for t in TERMS if t["g"] == g) for g, _ in GROUPS}
assert all(counts.values()), counts
gname = dict(GROUPS)
SHORT = {"basics":"Basics","fs":"Files","storage":"Storage","shell":"Shell","text":"Text","users":"Users","perms":"Permissions","proc":"Processes","services":"Services","pkg":"Packages","net":"Network","sec":"Security"}

def card(t):
    path, title = lesson(t["ref"])
    q = " ".join([t["term"], t.get("aka") or "", strip(t["simple"]), strip(t["behind"]), t.get("ex") or "", gname[t["g"]]]).lower()
    flow = ""
    if t["flow"]:
        steps = [s.strip() for s in t["flow"].split("→")]
        flow = '<ol class="gt-flow">' + '<li class="ar" aria-hidden="true">→</li>'.join(f"<li>{E(s)}</li>" for s in steps) + "</ol>"
    ex = f'<pre class="gt-ex"><span aria-hidden="true">$ </span><code>{E(t["ex"])}</code></pre>' if t["ex"] else ""
    aka = f' <small class="gt-aka">also: {E(t["aka"])}</small>' if t["aka"] else ""
    return (f'<article class="gt" id="{slugify(t["term"])}" data-g="{t["g"]}" data-q="{E(q)}">'
            f'<header><h3>{E(t["term"])}{aka}</h3><span class="gt-tag">{SHORT[t["g"]]}</span></header>'
            f'<p class="gt-simple">{t["simple"]}</p>'
            f'<div class="gt-behind"><b class="gt-bl">Behind the screen</b>{flow}<p>{t["behind"]}</p></div>'
            f'{ex}'
            f'<a class="gt-lesson" data-path="{path}/" href="../{path}/">Lesson {t["ref"]} · {E(title)}</a>'
            f'</article>')

BIG = '''<figure class="gt-map" aria-label="Big picture: the layers of a Linux system">
<h3 class="gt-map__t">What happens when you press Enter</h3>
<ol class="gt-layers">
  <li><b>You</b> type <code>grep ERROR app.log | wc -l</code></li>
  <li><b>Terminal</b> sends your keys through a pseudo-terminal (<code>/dev/pts/0</code>)</li>
  <li class="hl"><b>Shell (bash)</b> expands words, finds commands in PATH, creates the pipe, then fork + exec</li>
  <li><b>Programs</b> grep and wc run at the same time, joined by the pipe</li>
  <li class="sep" aria-hidden="true"><span>user space ↑</span><span>kernel space ↓</span></li>
  <li class="sc"><b>System calls</b> open · read · write · pipe · fork · execve · exit</li>
  <li class="k"><b>Kernel</b> files and inodes · scheduler · memory · drivers → disk, CPU, RAM, network</li>
</ol>
<figcaption>Most terms below live on one of these layers. Each card's <b>Behind the screen</b> box shows what really happens underneath the command you type.</figcaption>
</figure>'''

CSS = '''
.gt-toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:8px 0 6px}
.gl-search{display:flex;align-items:center;gap:8px;flex:1 1 280px;max-width:520px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.gl-search svg{width:18px;height:18px;color:var(--ink-3);flex:none}
.gl-search input{border:0;outline:0;background:none;font:inherit;color:var(--ink);width:100%;min-width:0}
.gt-chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px}
.gt-chips button{font:inherit;font-size:.85rem;padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--ink-2);cursor:pointer}
.gt-chips button[aria-pressed="true"]{background:var(--track);border-color:var(--track);color:#fff}
.gt-az{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 14px}
.gt-az a{font-family:var(--font-code);font-size:.8rem;padding:3px 7px;border-radius:6px;border:1px solid var(--line);color:var(--ink-2);text-decoration:none}
.gt-az a.off{opacity:.35;pointer-events:none}
.gt-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:12px}
.gt{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:flex;flex-direction:column;gap:8px;min-width:0;scroll-margin-top:90px}
.gt:target{outline:2px solid var(--track);outline-offset:2px}
.gt header{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
.gt h3{margin:0;font-family:var(--font-code);font-size:1rem;color:var(--track);overflow-wrap:anywhere}
.gt-aka{display:block;font-family:var(--font-body);font-weight:400;font-size:.78rem;color:var(--ink-3)}
.gt-tag{flex:none;font-size:.7rem;padding:2px 8px;border-radius:999px;background:var(--paper-2);color:var(--ink-3);border:1px solid var(--line);white-space:nowrap}
.gt-simple{margin:0;color:var(--ink)}
.gt code,.faq code{overflow-wrap:anywhere;word-break:break-word}
.gt-behind{background:var(--paper-2);border-left:3px solid var(--track);border-radius:8px;padding:8px 11px;font-size:.92rem;color:var(--ink-2)}
.gt-behind p{margin:4px 0 0}
.gt-bl{display:block;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--track)}
.gt-flow{list-style:none;padding:0;margin:6px 0 2px;display:flex;flex-wrap:wrap;gap:4px 2px;font-family:var(--font-code);font-size:.74rem}
.gt-flow li{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:2px 6px;color:var(--ink)}
.gt-flow li.ar{background:none;border:0;padding:2px 1px;color:var(--track);font-weight:700}
.gt-ex{margin:0;background:var(--board);color:var(--chalk);border-radius:8px;padding:8px 10px;font-family:var(--font-code);font-size:.8rem;white-space:pre-wrap;overflow-wrap:anywhere}
.gt-ex span{color:var(--saffron)}
.gt-ex code{background:none!important;color:inherit!important;padding:0!important;border:0!important;font:inherit}
.gt-ex{border:1px solid var(--line)}
.gt-lesson{margin-top:auto;font-size:.82rem;font-weight:700}
.gt-lesson.soon{color:var(--ink-3);font-weight:400;pointer-events:none}
.gt-map{margin:10px 0 18px;max-width:760px}
.gt-map__t{font-family:var(--font-head);font-size:1.15rem;margin:0 0 8px}
.gt-layers{list-style:none;margin:0;padding:0 0 0 22px;position:relative;display:flex;flex-direction:column;gap:6px}
.gt-layers::before{content:"";position:absolute;left:6px;top:6px;bottom:6px;border-left:2px dashed var(--track)}
.gt-layers li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px;font-size:.95rem;color:var(--ink-2)}
.gt-layers li b{color:var(--ink)}
.gt-layers li code{overflow-wrap:anywhere}
.gt-layers li.hl{background:var(--saffron-soft)}
.gt-layers li.sc{background:var(--blue-soft)}
.gt-layers li.k{background:var(--board);color:var(--chalk);border-color:var(--board)}
.gt-layers li.k b{color:var(--chalk)}
.gt-layers li.sep{background:none;border:0;border-top:2px solid var(--ink-3);border-radius:0;padding:2px 0 0;display:flex;justify-content:space-between;font-size:.75rem;color:var(--ink-3)}
.gt-map figcaption{font-size:.9rem;color:var(--ink-2);margin-top:6px}
#gt-empty{display:none}
'''

JS = '''
(function () {
  const q = document.getElementById("gl-q"), cards = Array.from(document.querySelectorAll(".gt")), cnt = document.getElementById("gl-count");
  const chips = Array.from(document.querySelectorAll(".gt-chips button")), conf = Array.from(document.querySelectorAll("#confused details"));
  let g = "all";
  // lesson links: link only to live lessons
  const live = new Set();
  try { (window.MP_COURSE.modules || []).forEach(m => m.lessons.forEach(l => { if (l.live) live.add(m.slug + "/" + l.slug + "/"); })); } catch (e) {}
  document.querySelectorAll(".gt-lesson").forEach(a => { if (!live.has(a.dataset.path)) { a.classList.add("soon"); a.removeAttribute("href"); a.textContent += " (coming soon)"; } });
  function run() {
    const s = q.value.trim().toLowerCase(); let n = 0;
    cards.forEach(c => { const on = (g === "all" || c.dataset.g === g) && (!s || c.dataset.q.includes(s)); c.hidden = !on; if (on) n++; });
    conf.forEach(d => { d.hidden = !!s && !d.textContent.toLowerCase().includes(s); });
    cnt.textContent = (s || g !== "all") ? n + " of " + cards.length + " terms" : cards.length + " terms";
    document.getElementById("gt-empty").style.display = n ? "none" : "block";
  }
  chips.forEach(b => b.addEventListener("click", () => { g = b.dataset.g; chips.forEach(x => x.setAttribute("aria-pressed", x === b)); run(); }));
  q.addEventListener("input", run);
  document.querySelectorAll(".gt-az a").forEach(a => a.addEventListener("click", () => { q.value = ""; g = "all"; chips.forEach(x => x.setAttribute("aria-pressed", x.dataset.g === "all")); run(); }));
  run();
})();
'''

def first_letter(t):
    c = t["term"].lstrip("/.~(").lstrip()[0].upper()
    return c if c.isalpha() else "#"
letters = {}
for t in TERMS:
    letters.setdefault(first_letter(t), slugify(t["term"]))

az = "".join(f'<a href="#{letters[L]}">{L}</a>' if L in letters else f'<a class="off">{L}</a>' for L in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
chips = '<button type="button" data-g="all" aria-pressed="true">All</button>' + "".join(
    f'<button type="button" data-g="{g}" aria-pressed="false">{E(n)} <small>({counts[g]})</small></button>' for g, n in GROUPS)
confused = "\n".join(f"<details><summary>{E(a)}</summary><p>{b}</p></details>" for a, b in CONFUSED)
cards = "\n".join(card(t) for t in TERMS)

TITLE = "Linux glossary: every term with what happens behind the screen"
DESC = f"Plain-English Linux glossary: {len(TERMS)} terms from kernel, shell and inode to pipes, permissions, signals, systemd, SSH, namespaces and cgroups. Each with a behind-the-screen explanation, an example command and the lesson where it is taught."
N = len(TERMS)
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(TITLE)} | MyPhatshala</title>
<meta name="description" content="{E(DESC)}">
<link rel="canonical" href="https://myphatshala.in/courses/linux/glossary/">
<meta property="og:title" content="Linux glossary · MyPhatshala">
<meta property="og:description" content="{E(DESC)}">
<link rel="icon" href="../../../assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../assets/css/style.css">
<link rel="stylesheet" href="../../../assets/css/lesson.css">
<style>{CSS}</style>
<script src="../../../assets/js/config.js"></script>
<script>try {{ const t = localStorage.getItem("mp-theme"); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"DefinedTermSet","name":"Linux glossary","url":"https://myphatshala.in/courses/linux/glossary/","hasDefinedTerm":[{"@type":"DefinedTerm","name":t["term"],"description":strip(t["simple"])} for t in TERMS]}, ensure_ascii=False)}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5906362345660187" crossorigin="anonymous"></script>
</head>
<body style="--track:{course.get('color') or '#0F766E'}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../../../" aria-label="MyPhatshala home"><img src="../../../assets/img/logo.svg" width="34" height="34" alt=""><span>My<b>Phatshala</b></span></a>
    <nav class="nav" aria-label="Main">
      <a href="../../../#tracks">All courses</a>
      <a href="../">Linux syllabus</a>
      <button class="theme-btn" id="theme-btn" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </nav>
  </div>
</header>
<main id="main">
<section class="lesson-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="../../../">Home</a><span>›</span><a href="../../../#track-devops">DevOps and Tools</a><span>›</span><a href="../">Linux</a><span>›</span><b>Glossary</b></nav>
    <h1>Linux glossary</h1>
    <p class="lead">Every Linux term in the course in plain words, and for each one, <b>what happens behind the screen</b>: which part of the system does the work, step by step. Search it, filter by topic, or jump by letter. Keep it open while you learn. {N} terms and {len(CONFUSED)} “often confused” pairs.</p>
    <div class="lesson-meta"><span>Linux</span><span>Reference</span><span>Beginner to Advanced</span><span>Free · no sign-up</span></div>
  </div>
</section>
<div class="wrap" style="padding-top:8px;padding-bottom:40px">
<div class="ad-slot" data-slot="top"></div>
<section class="part">
  {BIG}
  <div class="gt-toolbar">
    <label class="search gl-search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
      <input id="gl-q" type="search" placeholder="Search: inode, pipe, sudo, 2>&1, cgroup…" aria-label="Search the glossary">
    </label>
    <span class="muted" id="gl-count"></span>
  </div>
  <div class="gt-chips" role="group" aria-label="Filter by topic">{chips}</div>

  <h2 id="confused">Often confused</h2>
  <p class="muted">The pairs that trip up most students and interview candidates.</p>
  <div class="faq">
{confused}
  </div>
  <div class="ad-slot" data-slot="mid"></div>

  <h2 id="all">All terms A–Z</h2>
  <nav class="gt-az" aria-label="Jump to letter">{az}</nav>
  <div class="gt-grid">
{cards}
  </div>
  <p id="gt-empty" class="muted">No term matches. Try a shorter word, or clear the topic filter.</p>
</section>
<div class="ad-slot" data-slot="bottom"></div>
</div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <div><h4>MyPhatshala</h4><p>Free programming and IT lessons that show what happens behind the screen.</p></div>
    <div><h4>Learn</h4><a href="../../../#tracks">All courses</a><a href="../">Linux syllabus</a></div>
    <div><h4>Site</h4><a href="../../../about.html">About</a><a href="../../../contact.html">Contact</a><a href="../../../privacy.html">Privacy policy</a><a href="../../../disclaimer.html">Disclaimer</a></div>
    <div class="copyright">© MyPhatshala. All lesson content, diagrams and animations are original. Please do not copy without permission.</div>
  </div>
</footer>
<script src="../../../data/courses/linux.js"></script>
<script>{JS}</script>
<script src="../../../assets/js/ads.js"></script>
<script src="../../../assets/js/site.js"></script>
</body>
</html>
'''
out = os.path.join(ROOT, "courses/linux/glossary/index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(page)
print(f"wrote {out}: {N} terms, {len(CONFUSED)} confused pairs")
for g, n in GROUPS: print(f"  {counts[g]:3d}  {n}")
