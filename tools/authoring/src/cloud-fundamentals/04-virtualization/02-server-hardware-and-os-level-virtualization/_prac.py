from cloudkit import *
CA = 'l42_aws.txt'
PRAC = practical('Three parts. <b>A</b>: run and limit a container with Docker Desktop (UI) or the docker CLI. <b>B</b>: see what Docker does underneath — this layer has no UI. <b>C</b>: check hardware-assisted virtualization, paravirtual drivers and SR-IOV networking on your machine and in AWS. <b>Part C AWS outputs come from the moto emulator, which uses AWS’s published instance-type data.</b>', [
    ('A1 · Run an Alpine container', uicli(
        ['Install and open [[Docker Desktop]].', 'Top search bar: type <code>alpine</code> → [[Pull]].', '[[Images]] → alpine → [[Run]] (▶) → open [[Optional settings]] → Container name <code>tiffingo-box</code> → [[Run]].', '[[Containers]] → <code>tiffingo-box</code> → [[Exec]] tab → type <code>cat /etc/os-release</code>, <code>hostname</code>, <code>ps</code>.'],
        code('bash', 'terminal', 'docker run -it --name tiffingo-box --hostname tiffingo-box alpine sh\n# inside the container:\ncat /etc/os-release     # Alpine\nhostname                # tiffingo-box\nps                      # only sh (PID 1) and ps\nuname -r                # the kernel of the machine Docker runs on'), ui_label='UI way — Docker Desktop'),
        'On Windows/macOS <code>uname -r</code> shows the kernel of Docker Desktop’s hidden Linux VM — proof that containers need a Linux kernel underneath.'),
    ('A2 · Limit CPU and memory (cgroups)', uicli(
        ['Docker Desktop’s Run dialog has no per-container limit fields. [[Settings]] → [[Resources]] limits the <i>whole</i> Docker VM.', 'After starting a container with limits (CLI on the right), open [[Containers]] → the container → [[Stats]] to watch CPU % and memory against the limit.'],
        code('bash', 'terminal', 'docker run -d --name limited --cpus 0.5 --memory 256m nginx:alpine\ndocker stats --no-stream limited\ndocker inspect limited --format \'{{.HostConfig.NanoCpus}} {{.HostConfig.Memory}}\''), ui_label='UI way — Docker Desktop'),
        'Expect the memory limit to show as 256MiB. Per-container limits are set in the CLI or a Compose file — the UI only displays them.'),
    ('B1 · Underneath: namespaces by hand (Linux only)', uicli(
        ['There is no UI for this layer — it is exactly what Docker Desktop and Kubernetes hide from you. Use the terminal on a Linux machine, WSL2 or a cloud VM.'],
        code('bash', 'terminal (root)', "ls -l /proc/self/ns              # namespaces this shell lives in\nlsns | head                      # all namespaces (Docker containers appear here)\nsudo unshare --pid --uts --mount --fork --mount-proc \\\n  bash -c 'hostname lab-room; hostname; ps -e'\nhostname                         # unchanged outside"), ui_label='UI way'),
        'Own hostname, own process tree, same kernel — a container in one line. Lesson proof steps 3–6 show the real output.'),
    ('B2 · Underneath: a cgroup memory limit', uicli(
        ['No UI — Docker’s <code>--memory</code> flag writes exactly this setting for you.'],
        code('bash', 'terminal (systemd + cgroup v2)', "sudo systemd-run --scope -p MemoryMax=50M \\\n  python3 -c 'x = bytearray(200*1024*1024)'\n# → killed: the cgroup allows only 50 MB"), ui_label='UI way'),
        'The kernel’s out-of-memory killer stops only the process in that cgroup.'),
    ('C1 · Is hardware-assisted virtualization on?', uicli(
        ['Windows: [[Ctrl+Shift+Esc]] → [[Performance]] → [[CPU]] → [[Virtualization: Enabled]].', 'Inside a VM, the same screen shows [[Virtual machine: Yes]].'],
        code('bash', 'terminal', 'grep -c -E -w "vmx|svm" /proc/cpuinfo   # host: > 0 = VT-x / AMD-V available\nlscpu | grep -i hypervisor              # inside a VM: hypervisor vendor')),
        'Type 4 of this lesson. If it is disabled, every hypervisor on the machine is slower or refuses to run.'),
    ('C2 · Which paravirtual drivers is my VM using?', uicli(
        ['Windows VM: [[Device Manager]] → [[Network adapters]] — on EC2 you see [[Amazon Elastic Network Adapter]]; on KVM [[Red Hat VirtIO Ethernet Adapter]].', '[[Storage controllers]] shows the NVMe or VirtIO SCSI controller.'],
        code('bash', 'terminal inside a Linux VM', "lspci | grep -i -E 'virtio|elastic|nvme'\nethtool -i eth0 | head -2          # driver: ena / virtio_net\nls /sys/bus/virtio/devices 2>/dev/null")),
        'If you see e1000 or IDE instead, the VM is using slow emulated devices (type 6) — switch to virtio/ENA drivers.'),
    ('C3 · Hypervisor and SR-IOV networking per instance type (AWS)', uicli(
        ['AWS Console → [[EC2]] → left menu [[Instance types]].', 'Search <code>t2.micro</code>, then <code>m5.large</code>; open each and read the [[Details]] (hypervisor) and [[Networking]] sections ([[ENA support]], [[Network performance]]).', 'Compare: old t2 = Xen, no ENA; current families = Nitro, ENA required.'],
        code('bash', 'terminal', "aws ec2 describe-instance-types --instance-types t2.micro t3.micro m5.large c6gn.large p4d.24xlarge \\\n  --query 'InstanceTypes[].[InstanceType,Hypervisor,NetworkInfo.EnaSupport,NetworkInfo.NetworkPerformance]' \\\n  --output table", capsec(CA, '== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'ENA is SR-IOV-based enhanced networking: “required” means the instance can only boot with the ENA driver. Free — this only reads information.'),
    ('C4 · GPUs available to rent', uicli(
        ['[[EC2]] → [[Instance types]] → filter [[GPUs]] &gt; 0, or search <code>g5.xlarge</code> → [[Accelerators]] section shows the GPU model, count and memory.'],
        code('bash', 'terminal', "aws ec2 describe-instance-types --instance-types g5.xlarge p4d.24xlarge \\\n  --query 'InstanceTypes[].[InstanceType,GpuInfo.Gpus[0].Manufacturer,GpuInfo.Gpus[0].Name,GpuInfo.Gpus[0].Count,GpuInfo.Gpus[0].MemoryInfo.SizeInMiB]' \\\n  --output table", capsec(CA, '== 2)')), ui_label='UI way — AWS Management Console'),
        'A whole A10G or eight A100s are passed through to your instance (type 7, passthrough). Only reading data — no cost. Launching GPU instances is expensive; check the price first.')],
    cleanup='<code>docker rm -f tiffingo-box limited</code> (UI: [[Containers]] → select → [[Delete]]). Namespaces from <code>unshare</code> vanish when their shell exits. Part C only reads information and costs nothing.'.replace('[[', '<b>').replace(']]', '</b>'))
