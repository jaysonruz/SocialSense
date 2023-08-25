import requests
from pprint import pprint
import os
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_sapling_edits(text):
    try:
        response = requests.post(
            "https://api.sapling.ai/api/v1/edits",
            json={
                "key": os.environ.get("SAPLING_KEY"),
                "text": text,
                "session_id": 'test session'
            }
        )
        resp_json = response.json()
        if 200 <= response.status_code < 300:
            edits = resp_json['edits']
            return edits
        else:
            return f"Error: {resp_json}"
    except Exception as e:
        return f"Error: {e}"

if __name__=="__main__":
    # Example usage
    input_text = """Hatke Style. Hatke Enteertainment. Hatke Twist. New work for the launch of motog14 by Team 21N for @motorolain Client: @motorolain Marketing, Motorola: Shivam Ranjan, Girish Kumar Production House: @zulu.films Producers: @swarupnandaa, piscessom Director: @ishwarmuchhal Creative Team: @newkans, @ptamatta, @gulati_shagun, @yashika.in, @_swati_panwar__ Account Management Team: @bingeljell, @oyesimkhade, @guneet.kaur07 Founder & CEO: @the.malayali"""
    response = get_sapling_edits(input_text)
    pprint(response)
