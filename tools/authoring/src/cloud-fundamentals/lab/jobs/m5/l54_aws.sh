#!/bin/bash
# Lesson 5.4 — measure your own SLI: a Route 53 health check + CloudWatch alarm (moto emulator; real account: drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region us-east-1"
echo "== 1) health check: HTTPS GET /health every 30 s from AWS checkers around the world"
HC=$(aws $E route53 create-health-check --caller-reference tiffingo-$(date +%s) \
  --health-check-config Type=HTTPS,FullyQualifiedDomainName=tiffingo.in,ResourcePath=/health,RequestInterval=30,FailureThreshold=3 \
  --query 'HealthCheck.Id' --output text); echo "HealthCheckId: $HC"
aws $E route53 get-health-check --health-check-id $HC --query 'HealthCheck.HealthCheckConfig.[Type,FullyQualifiedDomainName,ResourcePath,RequestInterval,FailureThreshold]' --output text
echo "== 2) alarm when the site is unhealthy for 1 minute"
aws $E cloudwatch put-metric-alarm --alarm-name tiffingo-down --namespace AWS/Route53 --metric-name HealthCheckStatus \
  --dimensions Name=HealthCheckId,Value=$HC --statistic Minimum --period 60 --evaluation-periods 1 --threshold 1 --comparison-operator LessThanThreshold
aws $E cloudwatch describe-alarms --alarm-names tiffingo-down --query 'MetricAlarms[].[AlarmName,MetricName,Threshold,ComparisonOperator]' --output text
echo "== 3) clean up"
aws $E cloudwatch delete-alarms --alarm-names tiffingo-down; aws $E route53 delete-health-check --health-check-id $HC; echo "deleted: alarm, health check"
