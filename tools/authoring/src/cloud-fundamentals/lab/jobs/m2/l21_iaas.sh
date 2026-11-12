#!/bin/bash
# IaaS lab: launch, inspect, stop and terminate an EC2 VM with the AWS CLI.
# Runs against an AWS emulator (moto) when ENDPOINT is set; on a real account leave ENDPOINT empty.
R="aws ${ENDPOINT:+--endpoint-url $ENDPOINT} --region ap-south-1"
echo "== 1) who am I and which region"
$R sts get-caller-identity --output json
$R configure get region 2>/dev/null || echo "ap-south-1"
echo "== 2) find the latest Amazon Linux 2023 image (AMI) from the public SSM parameter"
AMI=$($R ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64 --query Parameter.Value --output text)
echo "$AMI"
echo "== 3) compare two instance types"
$R ec2 describe-instance-types --instance-types t3.micro t3.medium --query 'InstanceTypes[].[InstanceType,VCpuInfo.DefaultVCpus,MemoryInfo.SizeInMiB]' --output table
echo "== 4) create a key pair and save the private key"
$R ec2 create-key-pair --key-name tiffingo-key --query KeyMaterial --output text > tiffingo-key.pem
chmod 400 tiffingo-key.pem; ls -l tiffingo-key.pem | awk '{print $1, $NF}'; head -1 tiffingo-key.pem
echo "== 5) create a security group (firewall) that allows web traffic and SSH only from my IP"
SG=$($R ec2 create-security-group --group-name tiffingo-web --description "TiffinGo web server" --query GroupId --output text); echo "$SG"
$R ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 80 --cidr 0.0.0.0/0 --query 'SecurityGroupRules[0].[IpProtocol,FromPort,CidrIpv4]' --output text
$R ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 22 --cidr 203.0.113.25/32 --query 'SecurityGroupRules[0].[IpProtocol,FromPort,CidrIpv4]' --output text
echo "== 6) launch the VM with a start-up script (user data) that installs a web server"
cat > userdata.sh <<'U'
#!/bin/bash
dnf install -y nginx
echo "<h1>TiffinGo menu - served from EC2 in Mumbai</h1>" > /usr/share/nginx/html/index.html
systemctl enable --now nginx
U
IID=$($R ec2 run-instances --image-id "$AMI" --instance-type t3.micro --key-name tiffingo-key --security-group-ids "$SG" \
  --user-data file://userdata.sh --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=tiffingo-web},{Key=course,Value=cloud-fundamentals}]' \
  --query 'Instances[0].InstanceId' --output text); echo "$IID"
echo "== 7) check its state, size, zone and IPs"
$R ec2 describe-instances --instance-ids "$IID" --query 'Reservations[0].Instances[0].{State:State.Name,Type:InstanceType,Zone:Placement.AvailabilityZone,PrivateIP:PrivateIpAddress,PublicIP:PublicIpAddress,Image:ImageId}' --output table
echo "== 8) stop it (pay only for its disk while stopped), then start again"
$R ec2 stop-instances --instance-ids "$IID" --query 'StoppingInstances[0].[PreviousState.Name,CurrentState.Name]' --output text
$R ec2 start-instances --instance-ids "$IID" --query 'StartingInstances[0].[PreviousState.Name,CurrentState.Name]' --output text
echo "== 9) clean up: terminate the VM, delete the security group and key"
$R ec2 terminate-instances --instance-ids "$IID" --query 'TerminatingInstances[0].[PreviousState.Name,CurrentState.Name]' --output text
$R ec2 delete-security-group --group-id "$SG" && echo "security group deleted"
$R ec2 delete-key-pair --key-name tiffingo-key --query Return --output text 2>/dev/null; rm -f tiffingo-key.pem userdata.sh; echo "key pair deleted"
echo "== 10) proof nothing is left running"
$R ec2 describe-instances --filters Name=instance-state-name,Values=pending,running,stopping,stopped --query 'length(Reservations)' --output text
