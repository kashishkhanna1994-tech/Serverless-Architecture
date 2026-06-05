import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    # List all buckets
    response = s3.list_buckets()
    buckets = response['Buckets']

    unencrypted_buckets = []

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            # Check encryption configuration
            enc = s3.get_bucket_encryption(Bucket=bucket_name)

            # If encryption exists, skip
            rules = enc['ServerSideEncryptionConfiguration']['Rules']
            print(f"[ENCRYPTED] {bucket_name}")

        except s3.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']

            # If encryption not found
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                print(f"[UNENCRYPTED] {bucket_name}")
                unencrypted_buckets.append(bucket_name)
            else:
                print(f"[ERROR] {bucket_name} -> {e}")

    print("\n=== SUMMARY ===")
    if unencrypted_buckets:
        print("Buckets WITHOUT encryption:")
        for b in unencrypted_buckets:
            print(f"- {b}")
    else:
        print("All buckets are encrypted")

    return {
        "unencrypted_buckets": unencrypted_buckets
    }