import regex as re
# from gingerit.gingerit import GingerIt
try:
    from services.local_gingerit import GingerIt # import locally
except:
    from local_gingerit import GingerIt

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

# def check_correction_type(correction):
#     excluded_correction_types = ['Accept space','Accept comma addition','None']
#     for correction in ginger_cap['corrections']:
#         print("\t ------------------",correction['definition'])
#         if correction['definition'] in excluded_correction_types:
#             return False
#     return True

def fix_my_cap(text):
    """
    text: String 
    # 
    # takes the text as string and then removes hash tags and mentions and runs gingerit after that.
    
    """
    print(f"DEBUG: caption length = {len(text)}")
    
    try:
        parser = GingerIt()
        return parser.parse(remove_emoticons_hashtags_tags(text))
    except Exception as error:
    # handle the exception
        print("ERROR: An exception occurred:", error,end=" ")
        print("of Type:", type(error).__name__)
        
        return {'text':"", 
                'result':"",
                'corrections': []
                }
        
        
    

if __name__ == "__main__":
    text= """Aaah! Did you know, visiting Maldives is actually one of the easiest countries for us Indians? 🤫🤫 You don’t need a visa, you don’t need to pay for any e-visa. Just book your stay at a local public island instead of a resort island, and you can visit over a long weekend in under ₹40k! \nHere’s how: \n\nOff season flight tickets: ₹20k return \nStay~ 3500-6000/night \nActivities: Opt for free activities like snorkelling or paddle boarding \n\nI’ll talk more about how you can plan a trip and save money in detail, in reels that I post in the coming few days. Stay tuned! ❤️\n\nThis video is from a local island called 📍Fulidhoo in the Vaavu Atoll \n\nI’m wearing: \nOutfit from @styledivacouture \nManaged by @vblitzcommunications \nJewellery: @merakibymehek \n\n#maldives #visitmaldives #maldivesislands #maldivestrip #maldiveslovers #indiantravelblogger #travelblogger #travelphotography #travel #indiantraveller #indiantravelgram"""
    
    result = fix_my_cap(text[:])
    print(result)

# {'text': 'Gamers or hustlers. Corporate warriors or students. Whatever be their trip, what trips them up is a laptop that just cannot keep pace. for as part of “The Hunt for India’s Slowest Laptop” campaign by Team 21N.\n    Credits:\n    Brand:', 
# 'result': 'Gamers or hustlers. Corporate warriors or students. Whatever be their trip, what trips them up is a laptop that just cannot keep pace. Four as part of “The Hunt for India’s Slowest Laptop” campaign by Team 21N.\n    Credits:\n    Brand:', 
# 'corrections': [{'start': 135, 'text': 'for', 'correct': 'Four', 'definition': None}]}