#!/bin/bash
# TCP connect time (ms) from this computer to the EC2 API endpoint of each AWS Region; median of 5
for r in ap-south-1 ap-south-2 ap-southeast-1 me-central-1 eu-west-1 eu-central-1 us-east-1 us-west-2 sa-east-1 ap-southeast-2; do
  v=$(for i in 1 2 3 4 5; do curl -s -o /dev/null -w "%{time_connect}\n" --max-time 8 https://ec2.$r.amazonaws.com/; done | sort -n | sed -n 3p)
  printf "%-15s %6.0f ms\n" $r $(echo "$v*1000" | bc -l)
done
