import os
import requests

def download_image(url, save_path):
    if os.path.exists(save_path):
        print("DEBUG: Image already exists at", save_path)
        return

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print("DEBUG: Image downloaded successfully.")
        else:
            print("ERROR: Failed to download the image. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("ERROR: Error occurred during the request:", e)

if __name__ == "__main__":
    image_url = "https://instagram.fesb3-2.fna.fbcdn.net/v/t51.2885-15/364208468_1508629073274564_7815734344700095953_n.jpg?stp=dst-jpg_e15&_nc_ht=instagram.fesb3-2.fna.fbcdn.net&_nc_cat=1&_nc_ohc=Ce-80P4_aYoAX_ZiqkT&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfAGpL9C4MQYTPIOg8A1t7YLZKoHEAZ4A7bM9NUGwn0itg&oe=64C96DC0&_nc_sid=8b3546"
    save_path = "downloaded_image.jpg"

    download_image(image_url, save_path)
