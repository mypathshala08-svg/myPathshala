#!/bin/bash
# Lesson 5.3 — an Auto Scaling group with a target-tracking policy (moto emulator; real account: drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
AMI=$(aws $E ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
aws $E ec2 create-launch-template --launch-template-name menu-lt --launch-template-data "{\"ImageId\":\"$AMI\",\"InstanceType\":\"t3.micro\"}" >/dev/null
echo "== 1) Auto Scaling group: min 2, max 10, desired 2, across two AZs"
aws $E autoscaling create-auto-scaling-group --auto-scaling-group-name menu-asg --launch-template LaunchTemplateName=menu-lt \
  --min-size 2 --max-size 10 --desired-capacity 2 --availability-zones ap-south-1a ap-south-1b
aws $E autoscaling describe-auto-scaling-groups --auto-scaling-group-names menu-asg \
  --query 'AutoScalingGroups[].[AutoScalingGroupName,MinSize,DesiredCapacity,MaxSize,length(Instances)]' --output table
echo "== 2) target tracking: keep average CPU at 50%"
aws $E autoscaling put-scaling-policy --auto-scaling-group-name menu-asg --policy-name cpu50 --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{"PredefinedMetricSpecification":{"PredefinedMetricType":"ASGAverageCPUUtilization"},"TargetValue":50.0}' \
  >/dev/null
aws $E autoscaling describe-policies --auto-scaling-group-name menu-asg --query 'ScalingPolicies[].[PolicyName,PolicyType,TargetTrackingConfiguration.TargetValue]' --output text
echo "== 3) Diwali evening: scale out to 6 (what the policy would do when CPU stays high)"
aws $E autoscaling set-desired-capacity --auto-scaling-group-name menu-asg --desired-capacity 6
aws $E autoscaling describe-auto-scaling-groups --auto-scaling-group-names menu-asg \
  --query 'AutoScalingGroups[].[DesiredCapacity,length(Instances)]' --output text
echo "== 4) clean up"
aws $E autoscaling delete-auto-scaling-group --auto-scaling-group-name menu-asg --force-delete
aws $E ec2 delete-launch-template --launch-template-name menu-lt >/dev/null; echo "deleted: group (and its instances), launch template"
