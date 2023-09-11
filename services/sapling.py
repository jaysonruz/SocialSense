import requests
from pprint import pprint
import os
from dotenv import load_dotenv

# Try to import the function relatively, if not, import it absolutely
try:
    from services.sapling_to_ginger import sapling_to_gingerit_format
except ImportError:
    from sapling_to_ginger import sapling_to_gingerit_format
    print("locally imported")

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
    input_text = """this is my kimgdom come , thsi is my kindom cum."""
    response = get_sapling_edits(input_text)
    pprint(response)
    pprint(sapling_to_gingerit_format(response,input_text))
