#!/bin/bash
echo "== 1) does this CPU support hardware virtualization? (vmx = Intel VT-x, svm = AMD-V)"
echo "vmx/svm flags: $(grep -c -E -w 'vmx|svm' /proc/cpuinfo)"
echo "hypervisor flag: $(grep -c -w hypervisor /proc/cpuinfo) (non-zero = we are already inside a VM)"
lscpu | grep -E 'Hypervisor vendor|Virtualization type'
echo "== 2) a virtual disk is just a file: create a 10 GiB qcow2 disk"
qemu-img create -f qcow2 web1.qcow2 10G
echo "== 3) thin provisioning: virtual size vs space really used"
qemu-img info web1.qcow2 | grep -E '^(file format|virtual size|disk size)'
ls -lh web1.qcow2 | awk '{print "file on host:", $5}'
rm -f web1.qcow2
