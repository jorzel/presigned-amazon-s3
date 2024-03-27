
import logging
import boto3
from botocore.client import Config
import os
import requests    # To install: pip install requests
from botocore.exceptions import ClientError


def create_presigned_post(
        bucket_name, object_name, fields=None, conditions=None, expiration=3600,
    ):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    bucket = os.getenv("BUCKET")

    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name="eu-central-1",
    )
    try:
        response = s3_client.generate_presigned_post(
            bucket_name,
            object_name,
            Fields=fields,
            Conditions=[["starts-with", "$key", "user/job/"]],
            ExpiresIn=expiration,
        )
    except ClientError as e:
        print(e)
        return None

    # The response contains the presigned URL and required fields
    return response


# Generate a presigned S3 POST URL
object_name = "user/job/${filename}"
response = create_presigned_post(bucket, object_name)
if response is None:
    exit(1)

# Demonstrate how another Python program can use the presigned URL to upload a file
filepath = "./test.txt"
for i in range(1, 3):
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        fields = response['fields']
        fields['key'] = f"user/job/{i}.txt"
        http_response = requests.post(response['url'], data=fields, files=files)
# If successful, returns HTTP status code 204
print(http_response.text)
print(f'File upload HTTP status code: {http_response.status_code}')