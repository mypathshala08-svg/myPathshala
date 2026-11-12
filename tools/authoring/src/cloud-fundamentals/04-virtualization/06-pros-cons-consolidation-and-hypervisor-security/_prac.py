from cloudkit import *
C = 'l46.txt'; CA = 'l46_aws.txt'
def seca(a, b=None): return capsec(CA, a, b)
PRAC = practical('Part A checks and hardens your own machine; Part B hardens the virtualization settings that <b>you</b> control in AWS. Each step: UI way and CLI way. <b>Part B outputs come from the moto AWS emulator</b>; on a real account a Dedicated Host is billed per hour while allocated — release it right after the test.', [
    ('A1 · Check your CPU’s side-channel status (threat 2)', uicli(
        ['Windows: [[Windows Security]] → [[Device security]] → [[Core isolation details]] → see whether [[Memory integrity]] is on (it uses the Hyper-V hypervisor to protect the Windows kernel).', 'Detailed CPU mitigation status on Windows needs PowerShell (CLI on the right).'],
        code('bash', 'terminal', 'grep . /sys/devices/system/cpu/vulnerabilities/*\n\n# Windows PowerShell (as admin):\nInstall-Module SpeculationControl; Get-SpeculationControlSettings', capsec(C, '== 1)', '== 2)')), ui_label='UI way — Windows Security'),
        'Run it on your laptop and on a cloud VM and compare: “Not affected”, “Mitigation: …” or “Vulnerable”.'),
    ('A2 · Am I a VM, and is my host busy?', uicli(
        ['Windows VM: [[Task Manager]] → [[Performance]] → [[CPU]] shows [[Virtual machine: Yes]].', 'AWS: [[CloudWatch]] → [[Metrics]] → [[EC2]] → CPUUtilization; for t3 instances also [[CPUCreditBalance]] (low credits look like “steal”).'],
        code('bash', 'terminal', 'systemd-detect-virt      # kvm, amazon, microsoft, none…\ntop -bn1 | head -3       # %st = CPU stolen by the hypervisor for other VMs\nvmstat 1 5               # last column “st”')),
        'A high steal value means noisy neighbours or a burstable instance out of credits — right-size or move to a fixed-performance type.'),
    ('A3 · Remove devices you do not need (threat 1)', uicli(
        ['VirtualBox: select the VM → [[Settings]] → [[Audio]] → untick [[Enable Audio]].', '[[USB]] → untick [[Enable USB Controller]].', '[[Storage]] → select any [[Floppy]] controller → [[Remove]]; [[System]] → Boot Order → untick [[Floppy]].'],
        code('bash', 'terminal (KVM/libvirt)', "virsh dumpxml myvm | grep -E '<(disk|sound|input|controller) '\nvirsh edit myvm          # delete <sound>, floppy <disk>, unused <controller> entries\nVBoxManage modifyvm myvm --audio-enabled off --usb-ohci off --usb-ehci off --usb-xhci off"), ui_label='UI way — VirtualBox'),
        'Smaller device model = smaller VM-escape attack surface (the VENOM lesson). Older VirtualBox versions use <code>--audio none</code>.'),
    ('B1 · Which hypervisor runs each instance type?', uicli(
        ['[[EC2]] → [[Instance types]] → search <code>t2.micro</code>, <code>t3.micro</code>, <code>m5.large</code> → open each → [[Details]] shows [[Hypervisor]]: xen / nitro.'],
        code('bash', 'terminal', "aws ec2 describe-instance-types --instance-types t3.micro m5.large t2.micro \\\n  --query 'InstanceTypes[].[InstanceType,Hypervisor]' --output text", seca('== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'Prefer Nitro families: smaller hypervisor, I/O in dedicated hardware, no operator access.'),
    ('B2 · Encrypt every new EBS volume by default', uicli(
        ['[[EC2]] → [[Dashboard]] → right panel [[Account attributes]] → [[Data protection and security]].', '[[EBS encryption]] → [[Manage]] → tick [[Enable]] → [[Update EBS encryption]].', 'Repeat in every Region you use (the setting is per Region).'],
        code('bash', 'terminal', 'aws ec2 get-ebs-encryption-by-default\naws ec2 enable-ebs-encryption-by-default', seca('== 2)', '== 3)')), ui_label='UI way — AWS Management Console'),
        'All new volumes and snapshots are encrypted with keys from AWS KMS (Key Management Service) — a stolen snapshot (threat 4) is useless without the key.'),
    ('B3 · Require IMDSv2 (threat 4: stolen credentials)', uicli(
        ['New instance: [[Launch instances]] → [[Advanced details]] → [[Metadata version]] → [[V2 only (token required)]].', 'Existing instance: select it → [[Actions]] → [[Instance settings]] → [[Modify instance metadata options]] → IMDSv2 [[Required]] → [[Save]].', 'Account-wide default: [[EC2]] → [[Dashboard]] → [[Account attributes]] → [[Data protection and security]] → [[IMDS defaults]].'],
        code('bash', 'terminal', "aws ec2 run-instances --image-id $AMI --instance-type t3.micro \\\n  --metadata-options HttpTokens=required,HttpPutResponseHopLimit=1\n# existing instance:\naws ec2 modify-instance-metadata-options --instance-id i-… --http-tokens required", seca('== 3)', '== 4)')), ui_label='UI way — AWS Management Console'),
        'Blocks the classic SSRF attack (tricking a web app into fetching a URL for the attacker) that steals an instance’s role credentials from the metadata service (Lesson 2.1).'),
    ('B4 · No neighbours: allocate a Dedicated Host', uicli(
        ['[[EC2]] → [[Dedicated Hosts]] → [[Allocate Dedicated Host]].', 'Name <code>tiffingo-host</code>, instance family [[m5]], AZ [[ap-south-1a]], quantity 1 → [[Allocate]].', 'Release it straight away: select → [[Actions]] → [[Release host]].'],
        code('bash', 'terminal', "aws ec2 allocate-hosts --availability-zone ap-south-1a --instance-family m5 --quantity 1\naws ec2 describe-hosts --host-ids $H \\\n  --query 'Hosts[].[HostId,AvailabilityZone,State,HostProperties.InstanceFamily]' --output text\naws ec2 release-hosts --host-ids $H", seca('== 4)', '== 5)')), ui_label='UI way — AWS Management Console'),
        'A whole physical server for your account (threat 2 defence, and for per-core licences). Expensive — only when required.')],
    cleanup='Terminate the test instance ([[Instance state]] → [[Terminate instance]]) and release the Dedicated Host ([[Actions]] → [[Release host]]) — billing stops only after release. Keep EBS encryption by default and IMDSv2 <b>on</b> in real accounts.'.replace('[[', '<b>').replace(']]', '</b>'))
