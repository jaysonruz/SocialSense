import requests
import base64
import json

def download_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("Failed to download the image from the URL.")

def image_to_blob(image_content):
    return base64.b64encode(image_content).decode("utf-8")

def create_json_with_blob(image_blob):
    data = {
        "image_blob": image_blob
    }
    return json.dumps(data)

def convert_image_to_blob(url):
    try:
        image_content = download_image_from_url(url)
        image_blob = image_to_blob(image_content)
        # json_data = create_json_with_blob(image_blob)
        return image_blob
    except Exception as e:
        print("Error:", str(e))
        return None

if __name__ == "__main__":
    image_url = "https://instagram.fesb3-2.fna.fbcdn.net/v/t51.2885-15/364208468_1508629073274564_7815734344700095953_n.jpg?stp=dst-jpg_e15&_nc_ht=instagram.fesb3-2.fna.fbcdn.net&_nc_cat=1&_nc_ohc=Ce-80P4_aYoAX_ZiqkT&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfAGpL9C4MQYTPIOg8A1t7YLZKoHEAZ4A7bM9NUGwn0itg&oe=64C96DC0&_nc_sid=8b3546"
    resulting_json = convert_image_to_blob(image_url)
    print(resulting_json)
