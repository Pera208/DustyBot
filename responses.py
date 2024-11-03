import random

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return "Well, you're silent"
    elif 'hello' in lowered:
        return 'Hello there'
    elif 'sigma' in lowered:
        return 'so sigma'
    else:
        return random.choice(["default ahh response", "I don't know what to say yet", "I'm not super skibidi"])