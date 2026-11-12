#!/bin/bash
# Lesson 5.1 — Regions and AZs from the API (moto emulator; on a real account drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000}"
echo "== 1) AZ names vs AZ IDs in Mumbai"
aws $E --region ap-south-1 ec2 describe-availability-zones --query 'AvailabilityZones[].[ZoneName,ZoneId,State]' --output table
echo "== 2) the same instance type is offered in which AZs?"
aws $E --region ap-south-1 ec2 describe-instance-type-offerings --location-type availability-zone \
  --filters Name=instance-type,Values=m7i.large --query 'InstanceTypeOfferings[].Location' --output text
