def request_response(request, num = 1, upper_bound = 4, blank_ok = True):
    """
    Asks for choice. Makes checks until a 'valid' response is met. Returns a valid response as a string.
    """
    while True:
    
        response = input(request).strip()
        if response == "end":
            exit()
            break
        
        if len(response.split()) > 1: # Invalid string of integers (no spaces)
            print("Enter options without spaces, or leave blank for no selection")
            continue

        choices = make_choice_list(response)
        
        if blank_ok and choices == []: # If it's ok to return empty list and no choice has been made.
            break
        
        if choices[0] == -9: # Non-integer values
            print("Invalid 1")
            continue
              
        if len(choices) != num: # Check the desired number of responses is correct
            print("Incorrect number of choices, try again.")
            continue

        if check_duplicates(response, choices): # Duplicated values
            print("Duplicated, try again")
            continue
            
        out_of_bounds = False
        for choice in choices: # Check no values are out of bounds.
            if choice > upper_bound or choice < 0:
                print(f"A choice is out-of-bounds. Please select a number between 0 and {upper_bound}")
                out_of_bounds = True
        if out_of_bounds:
            continue
                
        break
            
    return choices # Could be a valid response, an empty string, or may have selected an out-of-bounds option
        
def make_choice_list(response):
    choices = []
    try:
        for c in response:
            choices.append(int(c))        
    except:
        print("Invalid options, integers only please.")
        return [-9]
        
    else:
        return choices            

def check_duplicates(response, choices):
    """
    Check if duplicate choices are made.
    """
    if len(set(choices)) != len(response):
        print("Duplicated choice!")
        return True
    else:
        return False
 