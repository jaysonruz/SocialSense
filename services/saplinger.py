# import requests
from pprint import pprint
import os
from dotenv import load_dotenv
from sapling import SaplingClient
import re


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

def remove_emoticons_hashtags_tags(text):
    # Remove emoticons
    text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+', '', text)

    # Remove hashtags and @tags
    text +=" "
    text = re.sub(r'[#@]\S+\s', '', text)

    # Remove anything inside parentheses
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove any trailing punctuations
    text = text.replace("@","").replace("#","")
    
    return text.strip()

def sapling_to_gingerit_format(original_text):
    sapling_response = get_sapling_edits(original_text)
    corrections = []

    for correction in sapling_response['edits']:
        start = int(correction['start'])+int(correction["sentence_start"]) 
        end = int(correction['end'])+int(correction["sentence_start"])
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

    return output,sapling_response

if __name__=="__main__":
    # Example usage
    input_text = """The numbers speak for themselves. 🎾 3x Calendar Grand Slams 🎾 37x Major Titles 🎾 122x Consecutive Singles Matches Won (and counting) Congratulations @diededegroot on another incredible run in New York. You are a true trailblazer and dominant force like no other. 🏆"""
    cleaned_input_text = remove_emoticons_hashtags_tags(input_text)
    print(cleaned_input_text)
    pprint(sapling_to_gingerit_format(cleaned_input_text))
