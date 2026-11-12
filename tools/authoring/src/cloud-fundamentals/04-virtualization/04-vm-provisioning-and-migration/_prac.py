from cloudkit import *
C = 'l44.txt'; CA = 'l44_aws.txt'
def sec(a, b=None): return capsec(C, a, b)
def seca(a, b=None): return capsec(CA, a, b)
PRAC = practical('Part A on your laptop with VirtualBox (UI) or qemu-img (CLI); Part B in AWS with the EC2 console (UI) or the AWS CLI. <b>Part B outputs come from the moto AWS emulator</b> — IDs differ on a real account. On a real account t3.micro is Free-Tier eligible; AMI snapshots cost a little per GB-month until deleted.', [
    ('A1 · Golden image and linked clones (type 2)', uicli(
        ['Prepare one VM (e.g. <code>tiffingo-lab</code> from Lesson 4.1) and shut it down.', 'Select it → [[Snapshots]] → [[Take]] → name <code>golden</code>.', 'Right-click the VM → [[Clone…]] → name <code>vm1</code> → Clone type [[Linked Clone]] → [[Finish]]. Repeat for <code>vm2</code>, <code>vm3</code>.', '[[File]] → [[Tools]] → [[Virtual Media Manager]]: each clone’s disk is tiny and linked to the parent.'],
        code('bash', 'terminal', 'qemu-img create -f qcow2 golden.qcow2 20G\nfor i in 1 2 3; do\n  qemu-img create -f qcow2 -b golden.qcow2 -F qcow2 vm$i.qcow2\ndone\nls -lh vm*.qcow2', sec('== 2)', '== 3)')), ui_label='UI way — VirtualBox'),
        '33 ms for three VM disks. VirtualBox “Linked Clone” and qcow2 backing files are the same copy-on-write idea.'),
    ('A2 · Snapshot before a risky change, then roll back', uicli(
        ['Select <code>vm1</code> → [[Snapshots]] → [[Take]] → <code>before-upgrade</code>.', 'Change something inside the VM.', 'Power off → select <code>before-upgrade</code> → [[Restore]].'],
        code('bash', 'terminal', 'qemu-img snapshot -c before-upgrade vm1.qcow2\nqemu-img snapshot -l vm1.qcow2\nqemu-img snapshot -a before-upgrade vm1.qcow2     # roll back', sec('== 3)', '== 4)')), ui_label='UI way — VirtualBox'),
        'Snapshots inside the disk file. They are not backups — if the file is lost, the snapshots go with it.'),
    ('A3 · Cold V2V: convert for VMware or Hyper-V (types 5 and 8)', uicli(
        ['VirtualBox: [[File]] → [[Tools]] → [[Virtual Media Manager]] → select the disk → [[Copy]] → format [[VMDK]] (VMware) or [[VHD]] (Hyper-V) → [[Finish]].', 'Or package the whole VM: [[File]] → [[Export Appliance…]] → format [[OVF 2.0]] → file <code>.ova</code> → [[Export]]. Import it on another machine with [[Import Appliance…]].'],
        code('bash', 'terminal', 'qemu-img convert -p -O vmdk golden.qcow2 golden.vmdk\nqemu-img convert -p -O vhdx golden.qcow2 golden.vhdx\nqemu-img convert -p -O raw  golden.qcow2 golden.raw\nqemu-img info golden.vmdk', sec('== 4)', '== 5)')), ui_label='UI way — VirtualBox'),
        'The file part of a cold migration. Drivers inside the guest may still need changing for the new hypervisor.'),
    ('B1 · Builder VM with user data (cloud-init)', uicli(
        ['AWS Console → [[EC2]] → [[Launch instances]] → name <code>menu-builder</code>.', 'AMI [[Amazon Linux 2023]], type [[t3.micro]], key pair, security group allowing HTTP 80 from your IP.', 'Expand [[Advanced details]] → scroll to [[User data]] → paste the script on the right.', '[[Launch instance]]; after ~2 minutes open <code>http://&lt;public-IP&gt;</code>: “TiffinGo menu v1”.'],
        code('bash', 'terminal', "AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \\\n  --query Parameter.Value --output text)\ncat > userdata.sh <<'UD'\n#!/bin/bash\ndnf install -y nginx && echo \"TiffinGo menu v1\" > /usr/share/nginx/html/index.html && systemctl enable --now nginx\nUD\nB=$(aws ec2 run-instances --image-id $AMI --instance-type t3.micro --user-data file://userdata.sh \\\n  --query 'Instances[0].InstanceId' --output text)", seca('== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'cloud-init runs the user-data script once, at first boot.'),
    ('B2 · Bake the golden AMI (type 3)', uicli(
        ['[[EC2]] → [[Instances]] → select <code>menu-builder</code>.', '[[Actions]] → [[Image and templates]] → [[Create image]].', 'Image name <code>tiffingo-menu-v1</code>, description “AL2023 + nginx + menu v1” → [[Create image]].', '[[Images]] → [[AMIs]]: wait until Status is [[Available]].'],
        code('bash', 'terminal', 'G=$(aws ec2 create-image --instance-id $B --name tiffingo-menu-v1 \\\n  --description "AL2023 + nginx + menu v1" --query ImageId --output text)\naws ec2 wait image-available --image-ids $G\naws ec2 describe-images --image-ids $G --query \'Images[].[ImageId,Name,State]\' --output table', seca('== 2)', '== 3)')), ui_label='UI way — AWS Management Console'),
        'By default the instance is rebooted for a consistent disk (“No reboot” is an option, at your own risk).'),
    ('B3 · Copy the AMI to another Region', uicli(
        ['[[AMIs]] → select <code>tiffingo-menu-v1</code> → [[Actions]] → [[Copy AMI]].', 'Destination Region [[Asia Pacific (Singapore) ap-southeast-1]] → [[Copy AMI]].', 'Switch the console Region to Singapore → [[AMIs]]: a new AMI ID appears.'],
        code('bash', 'terminal', 'aws ec2 copy-image --region ap-southeast-1 --source-region ap-south-1 \\\n  --source-image-id $G --name tiffingo-menu-v1', seca('== 3)', '== 4)')), ui_label='UI way — AWS Management Console'),
        'AMIs are Regional — copying is how you prepare disaster recovery or a new market.'),
    ('B4 · Write the launch template (the recipe)', uicli(
        ['[[EC2]] → [[Launch Templates]] → [[Create launch template]] → name <code>menu-lt</code>.', 'Application and OS Images: [[My AMIs]] → <code>tiffingo-menu-v1</code>; instance type [[t3.micro]].', '[[Advanced details]] → [[Metadata version]] → [[V2 only (token required)]] → [[Create launch template]].'],
        code('bash', 'terminal', 'aws ec2 create-launch-template --launch-template-name menu-lt \\\n  --launch-template-data "{\\"ImageId\\":\\"$G\\",\\"InstanceType\\":\\"t3.micro\\"}"', seca('== 4)', '== 5)')), ui_label='UI way — AWS Management Console'),
        'Version 1 of the recipe. Real templates also set security groups, IAM role and IMDSv2.'),
    ('B5 · Provision three identical VMs', uicli(
        ['[[Launch Templates]] → select <code>menu-lt</code> → [[Actions]] → [[Launch instance from template]].', 'Number of instances: <code>3</code> → [[Launch instance]].', '[[Instances]]: three instances with the same AMI ID.'],
        code('bash', 'terminal', "aws ec2 run-instances --launch-template LaunchTemplateName=menu-lt --count 3\naws ec2 describe-instances --instance-ids $IDS \\\n  --query 'Reservations[].Instances[].[InstanceId,ImageId,InstanceType,State.Name]' --output table", seca('== 5)', '== 6)')), ui_label='UI way — AWS Management Console'),
        'Identical by construction. An Auto Scaling group would do this automatically (type 4).'),
    ('B6 · Walk the lifecycle — a cold migration in one click', uicli(
        ['Select one instance → [[Instance state]] → [[Stop instance]] → state [[Stopping]] → [[Stopped]].', '[[Instance state]] → [[Start instance]] → [[Pending]] → [[Running]]; note the new public IP.'],
        code('bash', 'terminal', 'aws ec2 stop-instances  --instance-ids $ONE\naws ec2 start-instances --instance-ids $ONE', seca('== 6)', '== 7)')), ui_label='UI way — AWS Management Console'),
        'Stop/start usually lands on different hardware (type 5). The public IP changes unless it is an Elastic IP; instance-store data is lost; EBS data stays.')],
    cleanup='Console: [[Instances]] → select all four → [[Instance state]] → [[Terminate instance]]; [[AMIs]] → [[Actions]] → [[Deregister AMI]] in <b>both</b> Regions; then [[Snapshots]] → delete the snapshots behind each AMI (deregistering does not delete them); [[Launch Templates]] → [[Actions]] → [[Delete template]]. CLI: <code>terminate-instances</code>, <code>deregister-image</code> ×2, <code>delete-snapshot</code>, <code>delete-launch-template</code>. Locally: delete the .qcow2/.vmdk/.vhdx/.raw files and the cloned VMs.'.replace('[[', '<b>').replace(']]', '</b>'))
