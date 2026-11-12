#!/bin/bash
# Deeper IaaS lab: extra disk, snapshot, Elastic IP, IAM role (no keys on the server)
R="aws ${ENDPOINT:+--endpoint-url $ENDPOINT} --region ap-south-1"
AMI=$($R ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64 --query Parameter.Value --output text)
IID=$($R ec2 run-instances --image-id "$AMI" --instance-type t3.micro --placement AvailabilityZone=ap-south-1a --query 'Instances[0].InstanceId' --output text)
echo "== A) add a 20 GiB gp3 data disk in the SAME AZ and attach it"
VOL=$($R ec2 create-volume --availability-zone ap-south-1a --size 20 --volume-type gp3 --iops 3000 --throughput 125 --query VolumeId --output text); echo $VOL
$R ec2 attach-volume --volume-id $VOL --instance-id $IID --device /dev/sdf --query '[State,Device]' --output text
echo "== B) snapshot the data disk (incremental backup stored by AWS)"
SNAP=$($R ec2 create-snapshot --volume-id $VOL --description "tiffingo data backup" --query SnapshotId --output text); echo $SNAP
$R ec2 describe-snapshots --snapshot-ids $SNAP --query 'Snapshots[0].[SnapshotId,VolumeSize,State]' --output text
echo "== C) a fixed public address: allocate an Elastic IP and attach it"
ALLOC=$($R ec2 allocate-address --domain vpc --query 'AllocationId' --output text); echo "$ALLOC"
$R ec2 associate-address --instance-id $IID --allocation-id $ALLOC --query AssociationId --output text
echo "== D) give the server permissions with an IAM role (no access keys on the server)"
cat > trust.json <<'T'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}
T
$R iam create-role --role-name tiffingo-web-role --assume-role-policy-document file://trust.json --query Role.Arn --output text
$R iam attach-role-policy --role-name tiffingo-web-role --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess && echo "policy attached: AmazonS3ReadOnlyAccess"
$R iam create-instance-profile --instance-profile-name tiffingo-web-profile --query InstanceProfile.Arn --output text
$R iam add-role-to-instance-profile --instance-profile-name tiffingo-web-profile --role-name tiffingo-web-role && echo "role added to profile"
$R ec2 associate-iam-instance-profile --instance-id $IID --iam-instance-profile Name=tiffingo-web-profile --query 'IamInstanceProfileAssociation.[State,IamInstanceProfile.Arn]' --output text
echo "== E) require IMDSv2 (token-protected metadata service)"
$R ec2 modify-instance-metadata-options --instance-id $IID --http-tokens required --http-endpoint enabled --query 'InstanceMetadataOptions.[HttpTokens,HttpEndpoint]' --output text
echo "== F) clean up in the right order"
$R ec2 disassociate-address --association-id $($R ec2 describe-addresses --query 'Addresses[0].AssociationId' --output text) && echo "elastic IP detached"
$R ec2 release-address --allocation-id $ALLOC && echo "elastic IP released"
$R ec2 terminate-instances --instance-ids $IID --query 'TerminatingInstances[0].CurrentState.Name' --output text
$R ec2 wait instance-terminated --instance-ids $IID && echo "instance terminated (data volume now detached)"
$R ec2 delete-volume --volume-id $VOL && echo "data volume deleted"
$R ec2 delete-snapshot --snapshot-id $SNAP && echo "snapshot deleted"
$R iam remove-role-from-instance-profile --instance-profile-name tiffingo-web-profile --role-name tiffingo-web-role
$R iam delete-instance-profile --instance-profile-name tiffingo-web-profile
$R iam detach-role-policy --role-name tiffingo-web-role --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
$R iam delete-role --role-name tiffingo-web-role && echo "role and profile deleted"
rm -f trust.json
