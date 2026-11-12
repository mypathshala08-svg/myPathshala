#!/bin/bash
# Lesson 4.2 — hypervisor and SR-IOV networking (ENA) per instance type (moto emulator uses AWS's published instance-type data)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
echo "== 1) hypervisor, ENA (SR-IOV enhanced networking) and bandwidth per instance type"
aws $E ec2 describe-instance-types --instance-types t2.micro t3.micro m5.large c6gn.large p4d.24xlarge \
  --query 'InstanceTypes[].[InstanceType,Hypervisor,NetworkInfo.EnaSupport,NetworkInfo.NetworkPerformance]' --output table
echo "== 2) GPU instance types and their GPUs"
aws $E ec2 describe-instance-types --instance-types g5.xlarge p4d.24xlarge \
  --query 'InstanceTypes[].[InstanceType,GpuInfo.Gpus[0].Manufacturer,GpuInfo.Gpus[0].Name,GpuInfo.Gpus[0].Count,GpuInfo.Gpus[0].MemoryInfo.SizeInMiB]' --output table
