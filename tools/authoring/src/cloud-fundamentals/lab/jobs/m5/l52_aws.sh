#!/bin/bash
# Lesson 5.2 — shared vs dedicated tenancy and tagging per tenant (moto emulator; real account: drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
AMI=$(aws $E ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
echo "== 1) two instances, each tagged with the SaaS tenant it serves"
S=$(aws $E ec2 run-instances --image-id $AMI --instance-type m5.large --tag-specifications 'ResourceType=instance,Tags=[{Key=tenant,Value=pool}]' --query 'Instances[0].InstanceId' --output text)
D=$(aws $E ec2 run-instances --image-id $AMI --instance-type m5.large --tag-specifications 'ResourceType=instance,Tags=[{Key=tenant,Value=annapurna}]' --query 'Instances[0].InstanceId' --output text)
aws $E ec2 describe-instances --instance-ids $S $D --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`tenant`]|[0].Value]' --output table
echo "== 2) find everything that belongs to one tenant"
aws $E ec2 describe-instances --filters Name=tag:tenant,Values=annapurna --query 'Reservations[].Instances[].InstanceId' --output text
echo "== 3) clean up"
aws $E ec2 terminate-instances --instance-ids $S $D --query 'TerminatingInstances[].CurrentState.Name' --output text
