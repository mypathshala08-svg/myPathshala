#!/bin/bash
echo "== 1) a container shares the host kernel: compare kernel versions"
echo "host kernel:      $(uname -r)"
echo "inside container: $(unshare --pid --uts --mount --fork --mount-proc uname -r)"
echo "== 2) start time: isolated container-style process"
for i in 1 2 3; do s=$(date +%s%N); unshare --pid --uts --mount --fork --mount-proc true; e=$(date +%s%N); echo "run $i: $(( (e-s)/1000000 )) ms"; done
echo "== 3) image sizes (real downloads, HTTP headers)"
A=$(curl -s https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/latest-releases.yaml | grep -A8 'flavor: alpine-minirootfs' | awk '/size:/{print $2; exit}')
U=$(curl -sI https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img | awk 'tolower($1)=="content-length:"{print $2}' | tr -d '\r')
printf "Alpine minimal root filesystem (container base): %.1f MB\n" $(echo "$A/1048576" | bc -l)
printf "Ubuntu 24.04 cloud VM image (full OS + kernel):   %.0f MB\n" $(echo "$U/1048576" | bc -l)
