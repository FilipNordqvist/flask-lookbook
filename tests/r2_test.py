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


# Test 1: Lista filer i bucket
def list_files():
    response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME)
    if "Contents" in response:
        print("Filer i bucket:")
        for obj in response["Contents"]:
            print("-", obj["Key"])
    else:
        print("Bucket är tom!")


# Test 2: Ladda upp en liten testfil
def upload_test_file():
    s3.put_object(
        Bucket=R2_BUCKET_NAME, Key="test.txt", Body="Hej från Flask/R2!".encode("utf-8")
    )
    print("Testfil uppladdad!")


# Test 3: Ta bort testfil
def delete_test_file():
    s3.delete_object(Bucket=R2_BUCKET_NAME, Key="test.txt")
    print("Testfil borttagen!")


if __name__ == "__main__":
    list_files()
    upload_test_file()
    list_files()
    delete_test_file()
    list_files()
