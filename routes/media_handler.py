"""
Cloudflare R2 media handler for file uploads and management.

This module handles all interactions with Cloudflare R2 (S3-compatible object storage).
It provides functions to:
- Upload files to R2
- Generate public URLs for uploaded files
- Delete files from R2
- List files in the bucket

Cloudflare R2 is compatible with the S3 API, so we use boto3 (AWS SDK) to interact with it.
The boto3 library can work with any S3-compatible service by configuring a custom endpoint.
"""

import os
import uuid
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from flask import current_app
from config import Config


def get_r2_client():
    """
    Create and return a configured boto3 S3 client for Cloudflare R2.

    This function creates a boto3 client configured to work with Cloudflare R2.
    R2 is S3-compatible, so we use boto3's S3 client but point it to R2's endpoint.

    The client is configured with:
    - Custom endpoint URL (R2's S3-compatible API endpoint)
    - Access key ID and secret access key for authentication
    - Region (R2 doesn't use regions, but boto3 requires one, so we use 'auto')

    Returns:
        boto3.client: A configured S3 client for R2

    Raises:
        ValueError: If required R2 configuration is missing
    """
    # Validate that all required R2 configuration is present
    if not Config.R2_ACCESS_KEY_ID:
        raise ValueError("R2_ACCESS_KEY_ID environment variable is required")
    if not Config.R2_SECRET_ACCESS_KEY:
        raise ValueError("R2_SECRET_ACCESS_KEY environment variable is required")
    if not Config.R2_BUCKET_NAME:
        raise ValueError("R2_BUCKET_NAME environment variable is required")
    if not Config.R2_ENDPOINT_URL:
        raise ValueError("R2_ENDPOINT_URL environment variable is required")

    # Create an S3 client configured for Cloudflare R2
    # endpoint_url: R2's S3-compatible API endpoint
    # aws_access_key_id: Your R2 access key
    # aws_secret_access_key: Your R2 secret key
    # region_name: R2 doesn't use regions, but boto3 requires it, so we use 'auto'
    s3_client = boto3.client(
        "s3",
        endpoint_url=Config.R2_ENDPOINT_URL,
        aws_access_key_id=Config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
        region_name="auto",  # R2 doesn't use regions, but boto3 requires this
    )

    return s3_client


def upload_file_to_r2(file, folder="inspiration"):
    """
    Upload a file to Cloudflare R2.

    This function takes a file (from Flask's request.files) and uploads it to R2.
    It generates a unique filename to prevent collisions and stores it in a folder
    structure (default: "inspiration/").

    Args:
        file: A Flask FileStorage object (from request.files['file'])
        folder (str): The folder/prefix to store the file in (default: "inspiration")

    Returns:
        dict: A dictionary with:
            - 'success' (bool): Whether the upload succeeded
            - 'filename' (str): The unique filename generated
            - 'url' (str): The public URL to access the file
            - 'error' (str): Error message if upload failed

    Example:
        from flask import request
        result = upload_file_to_r2(request.files['image'])
        if result['success']:
            print(f"File uploaded: {result['url']}")
    """
    try:
        # Validate file was provided
        if not file or not file.filename:
            return {
                "success": False,
                "error": "No file provided",
            }

        # Get the original filename and extension
        original_filename = file.filename
        # os.path.splitext splits filename into (name, extension)
        # e.g., "photo.jpg" -> ("photo", ".jpg")
        _, file_extension = os.path.splitext(original_filename)

        # Generate a unique filename to prevent collisions
        # UUID4 generates a random unique identifier
        # We combine it with a timestamp and keep the original extension
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Create the full path in R2 (folder/filename)
        # This creates a folder structure in R2, even though R2 is flat storage
        r2_key = f"{folder}/{unique_filename}"

        # Get the R2 client
        s3_client = get_r2_client()

        # Reset file pointer to beginning (in case it was read before)
        file.seek(0)

        # Upload the file to R2
        # ExtraArgs can include metadata like ContentType
        # We try to preserve the original content type if available
        extra_args = {}
        if hasattr(file, "content_type") and file.content_type:
            extra_args["ContentType"] = file.content_type

        s3_client.upload_fileobj(
            file,  # The file object to upload
            Config.R2_BUCKET_NAME,  # The bucket name
            r2_key,  # The key (path) in the bucket
            ExtraArgs=extra_args,
        )

        # Generate the public URL
        # SECURITY NOTE: We use public URLs for the inspiration gallery because:
        # 1. The content is meant to be publicly accessible
        # 2. Public URLs provide better performance (CDN caching)
        # 3. They're simpler and more cost-effective than signed URLs
        # 
        # If you need private/restricted access in the future, consider:
        # - Using private buckets with signed URLs (expiring URLs)
        # - Implementing access control through your application
        # - Using Cloudflare R2's domain-level access controls
        #
        # If R2_PUBLIC_URL is configured, use it; otherwise construct from endpoint
        r2_public_url = Config.R2_PUBLIC_URL
        if r2_public_url:
            # If public URL ends with /, remove it to avoid double slashes
            base_url = r2_public_url.rstrip("/")
            public_url = f"{base_url}/{r2_key}"
        else:
            # Fallback: construct URL from endpoint (may not be publicly accessible)
            # This is a fallback - you should configure R2_PUBLIC_URL for production
            r2_endpoint = Config.R2_ENDPOINT_URL
            r2_bucket = Config.R2_BUCKET_NAME
            endpoint_base = r2_endpoint.replace(".r2.cloudflarestorage.com", ".r2.dev")
            public_url = f"{endpoint_base}/{r2_bucket}/{r2_key}"

        return {
            "success": True,
            "filename": unique_filename,
            "r2_key": r2_key,
            "url": public_url,
        }

    except (ClientError, BotoCoreError) as e:
        # Handle boto3-specific errors (network issues, authentication failures, etc.)
        return {
            "success": False,
            "error": f"R2 upload error: {str(e)}",
        }
    except Exception as e:
        # Handle any other unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
        }


def delete_file_from_r2(r2_key):
    """
    Delete a file from Cloudflare R2.

    Args:
        r2_key (str): The key (path) of the file in R2 to delete

    Returns:
        dict: A dictionary with:
            - 'success' (bool): Whether the deletion succeeded
            - 'error' (str): Error message if deletion failed
    """
    try:
        s3_client = get_r2_client()
        s3_client.delete_object(Bucket=Config.R2_BUCKET_NAME, Key=r2_key)

        return {"success": True}

    except (ClientError, BotoCoreError) as e:
        return {
            "success": False,
            "error": f"R2 delete error: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
        }


def list_files_in_r2(prefix="inspiration/"):
    """
    List all files in R2 with the given prefix.

    Args:
        prefix (str): The folder/prefix to list files from (default: "inspiration/")

    Returns:
        list: A list of file keys (paths) in R2
    """
    try:
        s3_client = get_r2_client()
        response = s3_client.list_objects_v2(
            Bucket=Config.R2_BUCKET_NAME, Prefix=prefix
        )

        # Extract file keys from the response
        # If 'Contents' exists, it contains the list of objects
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        return []

    except (ClientError, BotoCoreError) as e:
        # Log error but return empty list to avoid breaking the app
        current_app.logger.error(f"Error listing R2 files: {str(e)}")
        return []
    except Exception as e:
        current_app.logger.error(f"Unexpected error listing R2 files: {str(e)}")
        return []
