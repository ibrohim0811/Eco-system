import re

def validate_phone_number(phone_number: str) -> str | None:
    
    clean_phone = re.sub(r'\D', '', str(phone_number))

    
    if len(clean_phone) == 12 and clean_phone.startswith("998"):
        return clean_phone
        
    
    if len(clean_phone) == 9:
        return "998" + clean_phone

    return None
