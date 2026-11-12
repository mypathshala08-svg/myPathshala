#!/bin/bash
# Lesson 4.4 — provisioning from a golden image, lifecycle and copying images (moto emulator; on a real account drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000}"; R="--region ap-south-1"
AMI=$(aws $E $R ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
cat > /tmp/userdata.sh <<'UD'
#!/bin/bash
dnf install -y nginx && echo "TiffinGo menu v1" > /usr/share/nginx/html/index.html && systemctl enable --now nginx
UD
echo "== 1) launch a builder VM from the public base image, with cloud-init user data"
B=$(aws $E $R ec2 run-instances --image-id $AMI --instance-type t3.micro --user-data file:///tmp/userdata.sh --query 'Instances[0].InstanceId' --output text)
aws $E $R ec2 describe-instances --instance-ids $B --query 'Reservations[].Instances[].[InstanceId,ImageId,State.Name]' --output table
echo "== 2) capture it as our golden image (AMI)"
G=$(aws $E $R ec2 create-image --instance-id $B --name tiffingo-menu-v1 --description "AL2023 + nginx + menu v1" --query ImageId --output text)
aws $E $R ec2 describe-images --image-ids $G --query 'Images[].[ImageId,Name,State]' --output table
echo "== 3) copy the golden image to another Region (for DR / a new market)"
G2=$(aws $E --region ap-southeast-1 ec2 copy-image --source-region ap-south-1 --source-image-id $G --name tiffingo-menu-v1 --query ImageId --output text)
echo "copy in ap-southeast-1: $G2"
echo "== 4) a launch template = the provisioning recipe"
aws $E $R ec2 create-launch-template --launch-template-name menu-lt --launch-template-data "{\"ImageId\":\"$G\",\"InstanceType\":\"t3.micro\"}" --query 'LaunchTemplate.[LaunchTemplateName,LatestVersionNumber]' --output text
echo "== 5) provision 3 identical VMs from the recipe"
IDS=$(aws $E $R ec2 run-instances --launch-template LaunchTemplateName=menu-lt --count 3 --query 'Instances[].InstanceId' --output text)
aws $E $R ec2 describe-instances --instance-ids $IDS --query 'Reservations[].Instances[].[InstanceId,ImageId,InstanceType,State.Name]' --output table
echo "== 6) lifecycle: stop one, then start it again"
ONE=$(echo $IDS | awk '{print $1}')
aws $E $R ec2 stop-instances --instance-ids $ONE --query 'StoppingInstances[].[InstanceId,PreviousState.Name,CurrentState.Name]' --output text
aws $E $R ec2 start-instances --instance-ids $ONE --query 'StartingInstances[].[InstanceId,PreviousState.Name,CurrentState.Name]' --output text
echo "== 7) clean up (terminate, deregister images, delete template)"
aws $E $R ec2 terminate-instances --instance-ids $IDS $B --query 'TerminatingInstances[].CurrentState.Name' --output text
aws $E $R ec2 deregister-image --image-id $G >/dev/null; aws $E --region ap-southeast-1 ec2 deregister-image --image-id $G2 >/dev/null; aws $E $R ec2 delete-launch-template --launch-template-name menu-lt >/dev/null
echo "deleted: 4 instances, 2 images, 1 launch template"
