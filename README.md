```python
import os
import boto3
from botocore.client import Config
import requests    # To install: pip install requests


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

bucket_name = "testjorzel"
prefix = "mytest/"

# GET
presigned_get = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket_name, 'Key': "mytest/post_test1.txt"},
    ExpiresIn=60,
)
print('get', presigned_get)


def download_file(url):
    response_get = requests.get(url)
    print(f"Download, HTTP code: {response_get.status_code}, content: '{response_get.text}'")
    with open("presigned_get.txt", mode="wb") as file:
        file.write(response_get.content)


download_file(presigned_get)

# PUT
presigned_put = s3_client.generate_presigned_url(
    'put_object',
    Params={'Bucket': bucket_name, 'Key': prefix + "presigned_put.txt"},
    ExpiresIn=60,
)
print('put', presigned_put)

filepath = "test.txt"


def upload_put_file(filepath, presigned_put):
    with open(filepath, 'rb') as f:
        response_put = requests.put(presigned_put, data=f)
        print(f"Upload, HTTP code: {response_put.status_code}, content: '{response_put.text}'")


upload_put_file(filepath, presigned_put)


# POST
presigned_post = s3_client.generate_presigned_post(
    bucket_name,
    prefix + "${filename}",
    Fields=None,
    Conditions=[["starts-with", "$key", prefix]],
    ExpiresIn=60,
)
print(presigned_post)


def upload_post_file(filepath, object_name, policy):
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        fields = policy['fields']
        fields['key'] = object_name
        http_response = requests.post(policy['url'], data=fields, files=files)
    # If successful, returns HTTP status code 204
    print(f'File {object_name} upload HTTP status code: {http_response.status_code}, text: {http_response.text}')


filepath = "test.txt"
upload_post_file(filepath, 'test/post_test1.txt', presigned_post)
upload_post_file(filepath, 'test/post_test2.txt', presigned_post)

```