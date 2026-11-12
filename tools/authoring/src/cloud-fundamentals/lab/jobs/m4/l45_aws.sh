#!/bin/bash
# Lesson 4.5 — the same menu API as a VM, a container and a function (moto emulator; real account: drop --endpoint-url)
E="--endpoint-url ${ENDPOINT:-http://localhost:5000} --region ap-south-1"
cd /tmp; mkdir -p l45 && cd l45
ROLE=$(aws $E iam create-role --role-name menu-exec --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com","ecs-tasks.amazonaws.com"]},"Action":"sts:AssumeRole"}]}' --query Role.Arn --output text)
echo "== 1) as a VM (EC2): you choose OS image and size; you manage the OS"
AMI=$(aws $E ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
I=$(aws $E ec2 run-instances --image-id $AMI --instance-type t3.micro --query 'Instances[0].InstanceId' --output text)
aws $E ec2 describe-instances --instance-ids $I --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name]' --output text
echo "== 2) as a container (ECS on Fargate): you give an image + CPU/memory; AWS runs the host"
aws $E ecs create-cluster --cluster-name tiffingo --query 'cluster.[clusterName,status]' --output text
aws $E ecs register-task-definition --family menu-api --requires-compatibilities FARGATE --network-mode awsvpc --cpu 256 --memory 512 --execution-role-arn $ROLE \
  --container-definitions '[{"name":"menu","image":"public.ecr.aws/nginx/nginx:alpine","portMappings":[{"containerPort":80}],"essential":true}]' \
  --query 'taskDefinition.[family,revision,cpu,memory,requiresCompatibilities[0]]' --output text
echo "== 3) as a function (Lambda): you give only code; it runs per request"
cat > app.py <<'PY'
def handler(event, context):
    return {"statusCode": 200, "body": "TiffinGo menu: dal, roti, paneer"}
PY
python3 -c "import zipfile; z=zipfile.ZipFile('fn.zip','w'); z.write('app.py'); z.close()"
aws $E lambda create-function --function-name menu-fn --runtime python3.12 --handler app.handler --role $ROLE --zip-file fileb://fn.zip --memory-size 128 --timeout 5 \
  --query '[FunctionName,Runtime,MemorySize,Timeout,CodeSize]' --output text
echo "== 4) clean up"
aws $E lambda delete-function --function-name menu-fn >/dev/null
aws $E ecs deregister-task-definition --task-definition menu-api:1 >/dev/null; aws $E ecs delete-cluster --cluster tiffingo >/dev/null
aws $E ec2 terminate-instances --instance-ids $I --query 'TerminatingInstances[].CurrentState.Name' --output text
aws $E iam delete-role --role-name menu-exec; cd /tmp; rm -rf l45
echo "deleted: function, task definition, cluster, instance, role"
