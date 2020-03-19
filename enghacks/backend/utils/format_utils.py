import re

def is_integer(text):
    try: 
        int(text)
        return True
    except ValueError:
        return False

def format_phone(phone_number):
    # strip non-numeric characters
    phone = re.sub(r'\D', '', phone_number)
    # remove leading 1 (area codes never start with 1)
    phone = phone.lstrip('1')
    return '{}{}{}'.format(phone[0:3], phone[3:6], phone[6:])