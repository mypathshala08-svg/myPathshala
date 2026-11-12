#!/bin/bash
echo "== 1) network virtualization: two isolated network namespaces joined by a virtual cable (veth)"
ip netns add kitchen; ip netns add billing
ip link add veth-k type veth peer name veth-b
ip link set veth-k netns kitchen; ip link set veth-b netns billing
ip -n kitchen addr add 10.10.0.1/24 dev veth-k; ip -n billing addr add 10.10.0.2/24 dev veth-b
ip -n kitchen link set veth-k up; ip -n billing link set veth-b up; ip -n kitchen link set lo up; ip -n billing link set lo up
ip netns list
ip -n kitchen -brief addr show veth-k
ip netns exec kitchen ping -c 2 -W 1 10.10.0.2 | tail -3
echo "== 2) the host cannot see those interfaces"
ip -brief link | grep -c veth || true
ip netns del kitchen; ip netns del billing
echo "== 3) storage virtualization: pool two 200 MiB disks into one volume group (LVM)"
cd /tmp; truncate -s 200M d1.img d2.img; L1=$(losetup -f --show d1.img); L2=$(losetup -f --show d2.img)
pvcreate -q $L1 $L2; vgcreate -q pool $L1 $L2
pvs -o pv_name,vg_name,pv_size 2>/dev/null; vgs -o vg_name,pv_count,vg_size 2>/dev/null
vgremove -qy pool >/dev/null; pvremove -q $L1 $L2 >/dev/null; losetup -d $L1 $L2; rm -f d1.img d2.img
echo "== 4) copy-on-write: a 'linked clone' disk on top of a base image"
qemu-img create -q -f qcow2 base.qcow2 10G; qemu-img create -q -f qcow2 -b base.qcow2 -F qcow2 clone1.qcow2
qemu-img info clone1.qcow2 | grep -E '^(virtual size|disk size|backing file:)'
rm -f base.qcow2 clone1.qcow2
