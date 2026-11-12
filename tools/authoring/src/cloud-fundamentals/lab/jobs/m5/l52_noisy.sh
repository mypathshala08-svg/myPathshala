#!/bin/bash
# Lesson 5.2 — noisy neighbour on one shared CPU core, and the fix (weights/limits). Median of 3 runs.
B='import time
s=time.time(); x=0
for i in range(3_000_000): x+=i*i
print(round(time.time()-s,2))'
med(){ for i in 1 2 3; do taskset -c 0 python3 -c "$B"; done | sort -n | sed -n 2p; }
echo "== 1) tenant A alone on core 0 (seconds for the same job)"; echo "  $(med) s"
for i in 1 2 3; do taskset -c 0 python3 -c "while True: pass" & done; sleep 0.5
echo "== 2) three noisy tenants share core 0 with equal priority"; echo "  $(med) s"
pkill -f "while True"; sleep 0.3
for i in 1 2 3; do taskset -c 0 nice -n 19 python3 -c "while True: pass" & done; sleep 0.5
echo "== 3) same neighbours, but given a low CPU weight (nice 19 ≈ a small cgroup cpu.weight)"; echo "  $(med) s"
pkill -f "while True"
