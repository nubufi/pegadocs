import mimetypes
from typing import Tuple
import boto3
from botocore.exceptions import ClientError

from app.infra.config import settings

bucket_name = settings.S3_DATA_SOURCE_BUCKET_NAME
aws_region = settings.AWS_REGION

# Initialize S3 client
s3_client = boto3.client("s3", region_name=aws_region)


def generate_presigned_upload_url(
    object_key: str, expiration: int = 3600
) -> Tuple[str, str]:
    """
    Generate a presigned URL for uploading a file to S3.

    Args:
        object_key (str): The S3 object key (path) for the file
        expiration (int): URL expiration time in seconds (default: 1 hour)

    Returns:
        Tuple[str, str]: A tuple containing the presigned URL and the content type
    """
    try:
        content_type, _ = mimetypes.guess_type(object_key)
        if content_type is None:
            content_type = "application/octet-stream"
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expiration,
        )
        return response, content_type
    except ClientError as e:
        raise Exception(f"Error generating presigned URL: {str(e)}")
