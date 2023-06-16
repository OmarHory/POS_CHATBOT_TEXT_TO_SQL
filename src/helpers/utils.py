from datetime import datetime, timedelta
# from langdetect import detect
from gpt_api import send_to_gpt

def get_wsd(dd):
    dt = datetime.strptime(dd, "%Y-%m-%d")
    start = dt - timedelta(days=dt.weekday())
    return start

def get_wsd_string(today):
    day = today.strftime("%d")
    if day in ["11", "12", "13"]:
            day += "th"
    else:
            last_digit = day[-1]
    if last_digit == "1":
            day += "st"
    elif last_digit == "2":
            day += "nd"
    elif last_digit == "3":
            day += "rd"
    else:
            day += "th"
    date_string = today.strftime("%B ") + day + ", " + today.strftime("%Y")
    return date_string


def edit_prompt(prompt: str):
    if prompt[-1] != "?":
        prompt = prompt + "?"
    return prompt


def edit_response(edit_response: str):
    edit_response = edit_response.replace("_", " ").replace("SQLResult", 'data')

    return edit_response


def get_formatted_intent(intent):
    intent = intent.lower()
    if "orders".lower() in intent:
        intent = "Orders"

    if "Greeting".lower() in intent:
        intent = "Greeting"

    if "Farewell".lower() in intent:
        intent = "Farewell"

    if "Undefined".lower() in intent:
        intent = "Undefined"

    return intent


def translate_message(incoming_msg, language_map, prompt):
        # lang = detect(incoming_msg)
        user_language = 'English'
        for letter in language_map['Arabic']:
            if letter in incoming_msg:
                user_language = 'Arabic'
                break

        # user_language = language_map[lang]
        print("user_language is:", user_language)

        if user_language == 'Arabic':
            incoming_msg = send_to_gpt(prompt.format(user_language, incoming_msg))
            print(incoming_msg)
        
        return incoming_msg, user_language

def strip_message(incoming_msg):
    incoming_msg = incoming_msg.strip(".").strip('"').strip("'").strip(" ")
    return incoming_msg


# write a function to grab a specific key value from redis and return it, if not exists it should process a second parameter object store it on redis with the speficied key and return me the object, it should take an expiration time parameter
def get_from_redis(redis_client, key, object_to_store, expiration_time):
    if redis_client.exists(key):
        return redis_client.get(key)
    else:
        redis_client.setex(key, expiration_time, object_to_store)
        return object_to_store
    

def redis_hash_get_or_create(redis_client, key, object_to_store, expiration_time):
    for key_inner, value in object_to_store.items():
        if type(value) == list:
            object_to_store[key_inner] = ",".join(value)

    if redis_client.exists(key):
        dict_ = redis_client.hgetall(key)
        dict_ = {key.decode('utf-8'): value.decode('utf-8') for key, value in dict_.items()}
        return dict_
    else:
        redis_client.hset(key, mapping=object_to_store)
        redis_client.expire(key, expiration_time)
        return object_to_store



