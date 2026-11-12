#!/bin/bash
# Lesson 4.6 — hardening the virtualization layer you control in AWS (moto emulator; real account: drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
echo "== 1) which hypervisor does an instance type use?"
aws $E ec2 describe-instance-types --instance-types t3.micro m5.large t2.micro --query 'InstanceTypes[].[InstanceType,Hypervisor]' --output text | sort
echo "== 2) encrypt every new EBS volume in this Region by default"
aws $E ec2 get-ebs-encryption-by-default --output text
aws $E ec2 enable-ebs-encryption-by-default --output text
echo "== 3) launch with IMDSv2 required (blocks SSRF-style metadata theft)"
AMI=$(aws $E ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
I=$(aws $E ec2 run-instances --image-id $AMI --instance-type t3.micro --metadata-options HttpTokens=required,HttpPutResponseHopLimit=1 --query 'Instances[0].InstanceId' --output text)
aws $E ec2 describe-instances --instance-ids $I --query 'Reservations[].Instances[].[InstanceId,MetadataOptions.HttpTokens,MetadataOptions.HttpPutResponseHopLimit]' --output text
echo "== 4) a Dedicated Host: a whole physical server only for your account"
H=$(aws $E ec2 allocate-hosts --availability-zone ap-south-1a --instance-family m5 --quantity 1 --query 'HostIds[0]' --output text)
aws $E ec2 describe-hosts --host-ids $H --query 'Hosts[].[HostId,AvailabilityZone,State,HostProperties.InstanceFamily]' --output text
echo "== 5) clean up"
aws $E ec2 terminate-instances --instance-ids $I --query 'TerminatingInstances[].CurrentState.Name' --output text
aws $E ec2 release-hosts --host-ids $H --query 'Successful' --output text
aws $E ec2 disable-ebs-encryption-by-default --output text
