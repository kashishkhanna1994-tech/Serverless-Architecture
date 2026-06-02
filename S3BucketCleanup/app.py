import boto3
from datetime import datetime, timezone, timedelta

s3 = boto3.client('s3')

BUCKET_NAME = "s3-assignment-herovired"


def lambda_handler(event, context):

    objects = s3.list_objects_v2(Bucket="s3-assignment-herovired")

    if 'Contents' not in objects:
        print("Bucket is empty")
        return

    cutoff_date = datetime.now(timezone.utc) - timedelta(minutes=5)

    deleted_files = []

    for obj in objects['Contents']:

        if obj['LastModified'] < cutoff_date:

            s3.delete_object(
                Bucket="s3-assignment-herovired",
                Key=obj['Key']
            )

            deleted_files.append(obj['Key'])

            print(f"Deleted: {obj['Key']}")

    return {
        'statusCode': 200,
        'deleted_files': deleted_files
    }