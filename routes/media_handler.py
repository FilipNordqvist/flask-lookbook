import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv

# Ladda miljövariabler från .env-fil
load_dotenv()

# Hämta variabler från miljön
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")
R2_BUCKET_ENDPOINT = os.environ.get("R2_BUCKET_ENDPOINT")

# Skapa S3-klient (R2 är S3-kompatibelt)
s3 = boto3.client(
    "s3",
    endpoint_url=R2_BUCKET_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
)


# Ladda upp bild till R2
def upload_image_to_r2(file_name, file_data):
    s3.put_object(Bucket=R2_BUCKET_NAME, Key=file_name, Body=file_data)
    print(f"Bild {file_name} uppladdad till R2!")
