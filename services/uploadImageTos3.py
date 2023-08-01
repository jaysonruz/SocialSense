import requests
import boto3
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def upload_image_to_s3_from_url(image_url, bucket_name, s3_key, access_key, secret_key):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            s3.put_object(Body=response.content, Bucket=bucket_name, Key=s3_key, ACL='public-read')
            public_url = f'https://{bucket_name}.s3.amazonaws.com/{s3_key}'
            return public_url
        else:
            print("Failed to download the image. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error occurred while uploading to S3:", e)
        return None

if __name__ == "__main__":
    image_url = "https://instagram.fesb3-2.fna.fbcdn.net/v/t51.2885-15/364208468_1508629073274564_7815734344700095953_n.jpg?stp=dst-jpg_e15&_nc_ht=instagram.fesb3-2.fna.fbcdn.net&_nc_cat=1&_nc_ohc=Ce-80P4_aYoAX_ZiqkT&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfAGpL9C4MQYTPIOg8A1t7YLZKoHEAZ4A7bM9NUGwn0itg&oe=64C96DC0&_nc_sid=8b3546"
    s3_key = "uploaded_image.jpg"
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    aws_access_key = os.environ.get("AWS_ACCESS_KEY")
    aws_secret_key = os.environ.get("AWS_SECRET_KEY")

    public_url = upload_image_to_s3_from_url(image_url, bucket_name, s3_key, aws_access_key, aws_secret_key)
    if public_url:
        print("Image uploaded to S3 successfully. Public URL:", public_url)
    else:
        print("Failed to upload the image to S3.")
