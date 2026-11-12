#!/bin/bash
echo "== 1) CPU side-channel vulnerabilities the kernel knows about, and their status"
cd /sys/devices/system/cpu/vulnerabilities
for f in meltdown spectre_v1 spectre_v2 l1tf mds retbleed; do printf "%-12s %s\n" $f "$(cat $f | cut -c1-70)"; done
echo "total vulnerability entries: $(ls | wc -l)"
echo "== 2) server consolidation: five half-idle servers onto one host"
python3 - <<'P'
apps = {"Mail": 8, "Website": 15, "Accounts": 5, "HR": 3, "Backup": 10}   # % CPU of one server each
print("before: 5 physical servers, average CPU used:", round(sum(apps.values())/5, 1), "%")
print("after : 1 host with 5 VMs, CPU used:", sum(apps.values()), "%  (+ ~10% hypervisor/headroom target)")
watts = 300
print("power saved: 4 servers ×", watts, "W =", 4*watts, "W ≈", round(4*watts*24*365/1000), "kWh per year")
P
