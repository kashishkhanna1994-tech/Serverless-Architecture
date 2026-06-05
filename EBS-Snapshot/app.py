import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client('ec2')

# Volumes to back up
VOLUME_IDS = [
    "vol-0e301550b3c0534c9",
    "vol-0d9d37f92be8a57ba",
    "vol-0bfeab09803bf13e4"
]

RETENTION_DAYS = 20

def lambda_handler(event, context):

    created_snapshots = []

    # Create snapshots
    for volume_id in VOLUME_IDS:

        response = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=f"Automated backup for {volume_id}"
        )

        snapshot_id = response['SnapshotId']

        created_snapshots.append(snapshot_id)

        print(f"Created Snapshot: {snapshot_id} for {volume_id}")

        # Tag snapshot so we can identify it later
        ec2.create_tags(
            Resources=[snapshot_id],
            Tags=[
                {
                    'Key': 'CreatedBy',
                    'Value': 'LambdaBackup'
                }
            ]
        )

    # Delete old snapshots created by this Lambda
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    snapshots = ec2.describe_snapshots(
        OwnerIds=['self']
    )

    deleted_snapshots = []

    for snapshot in snapshots['Snapshots']:

        # Check tag
        tags = snapshot.get('Tags', [])

        lambda_snapshot = any(
            tag['Key'] == 'CreatedBy' and tag['Value'] == 'LambdaBackup'
            for tag in tags
        )

        if lambda_snapshot and snapshot['StartTime'] < cutoff_date:

            ec2.delete_snapshot(
                SnapshotId=snapshot['SnapshotId']
            )

            deleted_snapshots.append(snapshot['SnapshotId'])

            print(f"Deleted Snapshot: {snapshot['SnapshotId']}")

    return {
        "statusCode": 200,
        "created_snapshots": created_snapshots,
        "deleted_snapshots": deleted_snapshots
    }