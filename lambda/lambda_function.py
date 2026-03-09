#Uploader

import json
import boto3
import base64
import time

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

BUCKET_NAME = "aadil-image-processing-project"
TABLE_NAME = "JobApplications"

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):

    try:

        body = json.loads(event['body'])

        name = body.get("name")
        email = body.get("email")
        file_data = body.get("file")
        file_name = body.get("file_name")

        if not file_data:
            return {
                "statusCode":400,
                "body":json.dumps({"error":"Resume file missing"})
            }

        file_bytes = base64.b64decode(file_data)

        key = f"resumes/{int(time.time())}_{file_name}"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=file_bytes,
            ContentType="application/pdf"
        )

        resume_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"

        table.put_item(
            Item={
                "email": email,
                "name": name,
                "resume_key": key,
                "resume_url": resume_url,
                "applied_at": time.ctime()
            }
        )

        return {
            "statusCode":200,
            "headers":{
                "Access-Control-Allow-Origin":"*"
            },
            "body":json.dumps({
                "message":"Application submitted successfully"
            })
        }

    except Exception as e:

        return {
            "statusCode":500,
            "body":json.dumps(str(e))
        }


#getapplicants

import json
import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table("JobApplications")

def lambda_handler(event, context):

    try:

        response = table.scan()

        applicants = response['Items']

        return {
            "statusCode":200,
            "headers":{
                "Access-Control-Allow-Origin":"*"
            },
            "body":json.dumps(applicants)
        }

    except Exception as e:

        return {
            "statusCode":500,
            "body":json.dumps(str(e))
        }
