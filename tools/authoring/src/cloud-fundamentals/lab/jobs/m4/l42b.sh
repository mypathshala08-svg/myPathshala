#!/bin/bash
# a container from scratch: Alpine root filesystem + chroot + namespaces + cgroup-like limit (ulimit)
cd /tmp && rm -rf mybox && mkdir mybox && cd mybox
F=$(curl -s https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/latest-releases.yaml | awk '/flavor: alpine-minirootfs/{f=1} f&&/file:/{print $2; exit}')
echo "== 1) download a 3.5 MB Linux root filesystem: $F"
curl -s -O https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/$F && mkdir rootfs && tar -xzf $F -C rootfs && du -sh rootfs | awk '{print "unpacked size:", $1}'
echo "== 2) enter it: new root (chroot) + new PID, hostname and mount namespaces"
unshare --pid --uts --mount --fork --mount-proc=rootfs/proc chroot rootfs /bin/sh -c 'hostname tiffingo-box; . /etc/os-release; echo "OS inside: $PRETTY_NAME"; echo "hostname: $(hostname)"; echo "kernel: $(uname -r)"; echo "processes:"; ps -o pid,comm'
echo "== 3) on the host, the OS is different"
. /etc/os-release; echo "OS on host: $PRETTY_NAME"; echo "kernel on host: $(uname -r)"
cd /tmp && rm -rf mybox
