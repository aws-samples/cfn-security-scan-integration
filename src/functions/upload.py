"""
 Upload the report S3 bucket
 
 Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 SPDX-License-Identifier: MIT-0
"""
import json
import os
import urllib.parse
import boto3


def upload_report(tool: str, report, create_at: str, source_repository: str, source_branch: str):

    bucket = os.environ['ReportsS3Bucket']
    branch_short = source_branch.split("/")[2]
    key = f"{tool}-report/repo:{source_repository}/branch:{branch_short}/{tool}-{create_at}.json"

    s3 = boto3.client('s3')
    response = s3.put_object(Bucket=bucket,
                             Body=json.dumps(report),
                             Key=key,
                             ServerSideEncryption='AES256')

    region = s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
    url = f"https://s3.console.aws.amazon.com/s3/object/{bucket}/{key}?region={region}"
    return(url)
