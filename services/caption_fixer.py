import regex as re

try:
    from services.saplinger import sapling_to_gingerit_format 
except:
    from saplinger import sapling_to_gingerit_format


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


def fix_my_cap(text):
    """
    text: String 
    # 
    # takes the text as string and then removes hash tags and mentions and runs gingerit after that.
    
    """
    print(f"DEBUG: caption length = {len(text)}")
    
    try:
        # parser = GingerIt()
        # return parser.parse(remove_emoticons_hashtags_tags(text))
        # emoticonsless_text=remove_emoticons_hashtags_tags(text)
        return sapling_to_gingerit_format(text)
        
    except Exception as error:
    # handle the exception
        print("ERROR: An exception occurred:", error,end=" ")
        print("of Type:", type(error).__name__)
        
        return {'text':"", 
                'result':"",
                'corrections': []
                }
        
        
    

if __name__ == "__main__":
    text= """#GoBeyondSpeed. To launch the moto g54 5G, a phone with some truly wild specs in its class, saying howdy to the wild west, was but natural. Our latest for @motorolain Client: @motorolain Marketing, Motorola: Shivam Ranjan , Girish Kumar Director: Yogesh Agarwal Production House: @zulu.films Executive Producers: @swarupnandaa , somdadda Creative Team: @newkans , @ptamatta , @adifyi , @gulati_shagun , @yashika.in , @_swati_panwar__ Account Management Team: @bingeljell , @guneet.kaur07 , @trp_98 Founder & CEO: @the.malayali { if win post this }"""
    
    result = fix_my_cap(text[:])
    print(result)

# {'text': 'Gamers or hustlers. Corporate warriors or students. Whatever be their trip, what trips them up is a laptop that just cannot keep pace. for as part of “The Hunt for India’s Slowest Laptop” campaign by Team 21N.\n    Credits:\n    Brand:', 
# 'result': 'Gamers or hustlers. Corporate warriors or students. Whatever be their trip, what trips them up is a laptop that just cannot keep pace. Four as part of “The Hunt for India’s Slowest Laptop” campaign by Team 21N.\n    Credits:\n    Brand:', 
# 'corrections': [{'start': 135, 'text': 'for', 'correct': 'Four', 'definition': None}]}