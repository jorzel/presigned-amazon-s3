
import os
import sys

import boto3
from botocore.client import Config
import requests    # To install: pip install requests
from botocore.exceptions import ClientError


# take expiration from command line arguments if passed
if len(sys.argv) > 1:
    expiration = int(sys.argv[1])
else:
    expiration = 3600


ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
bucket_name = "testjorzel"
region = "eu-central-1"

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name=region,
)

prefix = "myfolder/"

presigned_post = s3_client.generate_presigned_post(
    bucket_name,
    prefix + "${filename}",
    Fields=None,
    Conditions=[["starts-with", "$key", prefix]],
    ExpiresIn=expiration,
)

presigned_get = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket_name, 'Key': prefix + "put.txt"},
    ExpiresIn=expiration,
)
print('get', presigned_get)
presigned_put = s3_client.generate_presigned_url(
    'put_object',
    Params={'Bucket': bucket_name, 'Key': prefix + "put.txt"},
    ExpiresIn=expiration,
)
print('put', presigned_put)

filepath = "./test.txt"
with open(filepath, 'rb') as f:
    response_put = requests.put(presigned_put, data=f)
    print(response_put.status_code, response_put.text)
response_get = requests.get(presigned_get)
print(response_get.status_code, response_get.text)
with open("presigned_get.txt", mode="wb") as file:
    file.write(response_get.content)


def upload_file(filepath, object_name, policy):
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        fields = policy['fields']
        fields['key'] = object_name
        http_response = requests.post(policy['url'], data=fields, files=files)
    # If successful, returns HTTP status code 204
    print(f'File upload HTTP status code: {http_response.status_code}, text: {http_response.text}')


# filepath = "./test.txt"
# upload_file(filepath, 'myfolder/test1.txt', policy)  # should be success