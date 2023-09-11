# import requests
from pprint import pprint
import os
from dotenv import load_dotenv
from sapling import SaplingClient


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_sapling_edits(text):
    api_key = os.environ.get("SAPLING_KEY")
    client = SaplingClient(api_key=api_key)
    edits = client.edits(text, session_id='test_session')
    return edits

def apply_edits(edits,text):
    text = str(text)
    edits = sorted(edits, key=lambda e: (e['sentence_start'] + e['start']), reverse=True)
    for edit in edits:
        start = edit['sentence_start'] + edit['start']
        end = edit['sentence_start'] + edit['end']
        if start > len(text) or end > len(text):
            print(f'Edit start:{start}/end:{end} outside of bounds of text:{text}')
            continue
        text = text[: start] + edit['replacement'] + text[end:]
    return text

def sapling_to_gingerit_format(original_text):
    sapling_response = get_sapling_edits(original_text)
    corrections = []

    for correction in sapling_response['edits']:
        start = correction['start'] 
        end = correction['end']
        replacement = correction['replacement']
        general_error_type = correction['general_error_type']

        correction_obj = {
            "start": start,
            "text": original_text[start:end],
            "correct": replacement,
            "definition": general_error_type
        }

        corrections.append(correction_obj)

    # Create the desired output format
    output = {
        "text": original_text,
        "result": apply_edits(sapling_response['edits'],original_text),
        "corrections": corrections
    }

    return output

if __name__=="__main__":
    # Example usage
    input_text = """this is my kimgdom come , thsi is my kindom cum."""
    pprint(sapling_to_gingerit_format(input_text))
