#!/bin/bash
# Lesson 4.3 — network + storage virtualization in AWS (run against moto emulator; on a real account drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
echo "== 1) a virtual network (VPC) with its own private address range"
VPC=$(aws $E ec2 create-vpc --cidr-block 10.10.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=tiffingo-vpc}]' --query Vpc.VpcId --output text); echo "VpcId: $VPC"
echo "== 2) two subnets = two virtual network segments (kitchen, billing)"
S1=$(aws $E ec2 create-subnet --vpc-id $VPC --cidr-block 10.10.1.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
S2=$(aws $E ec2 create-subnet --vpc-id $VPC --cidr-block 10.10.2.0/24 --availability-zone ap-south-1b --query Subnet.SubnetId --output text)
aws $E ec2 describe-subnets --filters Name=vpc-id,Values=$VPC --query 'Subnets[].[CidrBlock,AvailabilityZone,AvailableIpAddressCount]' --output table
echo "== 3) the VPC's built-in router: local route covers the whole VPC"
aws $E ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC --query 'RouteTables[].Routes[].[DestinationCidrBlock,GatewayId,State]' --output table
echo "== 4) a virtual firewall (security group) — a rule, not a box"
SG=$(aws $E ec2 create-security-group --group-name kitchen-sg --description "kitchen API" --vpc-id $VPC --query GroupId --output text)
aws $E ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 443 --cidr 10.10.2.0/24 >/dev/null
aws $E ec2 describe-security-groups --group-ids $SG --query 'SecurityGroups[].IpPermissions[].[IpProtocol,FromPort,IpRanges[0].CidrIp]' --output table
echo "== 5) virtual block storage: a 20 GiB gp3 volume carved from the AZ's storage pool"
V=$(aws $E ec2 create-volume --availability-zone ap-south-1a --size 20 --volume-type gp3 --query VolumeId --output text)
aws $E ec2 describe-volumes --volume-ids $V --query 'Volumes[].[VolumeId,Size,VolumeType,State,AvailabilityZone]' --output table
echo "== 6) snapshot (copy-on-write, stored in S3) and a new volume from it in another AZ"
SN=$(aws $E ec2 create-snapshot --volume-id $V --description "before menu upgrade" --query SnapshotId --output text); echo "SnapshotId: $SN"
V2=$(aws $E ec2 create-volume --availability-zone ap-south-1b --snapshot-id $SN --volume-type gp3 --query VolumeId --output text)
aws $E ec2 describe-volumes --volume-ids $V2 --query 'Volumes[].[VolumeId,Size,SnapshotId,AvailabilityZone]' --output table
echo "== 7) clean up"
aws $E ec2 delete-volume --volume-id $V2; aws $E ec2 delete-volume --volume-id $V; aws $E ec2 delete-snapshot --snapshot-id $SN
aws $E ec2 delete-security-group --group-id $SG; aws $E ec2 delete-subnet --subnet-id $S1; aws $E ec2 delete-subnet --subnet-id $S2; aws $E ec2 delete-vpc --vpc-id $VPC
echo "deleted: volumes, snapshot, security group, subnets, VPC"
