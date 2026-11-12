#!/bin/bash
echo "== 1) the namespaces every Linux process lives in"
ls -l /proc/self/ns | awk 'NR>1{print $9, $11}'
echo "== 2) host view: how many processes and what hostname?"
echo "processes: $(ps -e --no-headers | wc -l)   hostname: $(hostname)"
echo "== 3) start a shell in NEW pid, uts and mount namespaces (what Docker does)"
unshare --pid --uts --mount --fork --mount-proc bash -c 'hostname tiffingo-box; echo "inside: hostname=$(hostname)"; echo "inside: processes visible:"; ps -e -o pid,comm --no-headers; true'
echo "== 4) back on the host: hostname unchanged"
echo "host hostname: $(hostname)"
echo "== 5) time to start an isolated environment"
s=$(date +%s%N); unshare --pid --uts --mount --fork --mount-proc true; e=$(date +%s%N); echo "unshare start + exit: $(( (e-s)/1000000 )) ms"
