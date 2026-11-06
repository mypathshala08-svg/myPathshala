import boto3
s=boto3.client('s3',endpoint_url='http://127.0.0.1:5050',aws_access_key_id='lab',aws_secret_access_key='labsecret',region_name='us-east-1')
b='tiffingo-lake'
s.copy_object(Bucket=b,CopySource={'Bucket':b,'Key':'warehouse/orders_s3/order_date=2026-10-07/000000_0'},Key='warehouse/orders_s3/order_date=2026-10-09/000000_0')
print('copied')
