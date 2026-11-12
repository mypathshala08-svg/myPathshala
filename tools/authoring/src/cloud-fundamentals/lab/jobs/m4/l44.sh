#!/bin/bash
cd /tmp
echo "== 1) a golden base image (stands in for a real OS image)"
qemu-img create -q -f qcow2 golden.qcow2 20G && qemu-img info golden.qcow2 | grep -E '^(virtual size|disk size)'
echo "== 2) provision 3 VMs as linked clones (copy-on-write) and time it"
s=$(date +%s%N); for i in 1 2 3; do qemu-img create -q -f qcow2 -b golden.qcow2 -F qcow2 vm$i.qcow2; done; e=$(date +%s%N)
echo "3 clones created in $(( (e-s)/1000000 )) ms"; ls -lh vm*.qcow2 | awk '{print $9, $5}'
echo "== 3) snapshot a VM disk before an upgrade, then list snapshots"
qemu-img snapshot -c before-upgrade vm1.qcow2 && qemu-img snapshot -l vm1.qcow2 | awk 'NR>2{print "snapshot:", $2}'
echo "== 4) convert a disk for another hypervisor (cold migration)"
for f in vmdk vhdx raw; do qemu-img convert -O $f golden.qcow2 golden.$f; done
qemu-img info golden.vmdk | grep '^file format'; qemu-img info golden.vhdx | grep '^file format'; qemu-img info golden.raw | grep -E '^(file format|disk size)'
rm -f golden.* vm*.qcow2
echo "== 5) size of a real cloud OS image (Ubuntu 24.04 server, cloud-images.ubuntu.com)"
curl -sI https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img | awk 'tolower($1)=="content-length:"{printf "%.0f MB\n", $2/1048576} tolower($1)=="last-modified:"{print "updated:", $3,$4,$5}'
