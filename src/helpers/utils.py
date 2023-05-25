from datetime import datetime, timedelta


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
    prompt = (
        prompt.lower()
        .replace(" prices ", " border cost ")
        .replace(" price ", " border cost ")
        .replace(" pricing ", " border cost ")
    )
    return prompt


def edit_response(edit_response: str):
    edit_response = edit_response.replace("_", " ").replace("SQLResult", 'data')

    return edit_response


def get_formatted_intent(intent):
    intent = intent.lower()
    if "demand of avocado".lower() in intent:
        intent = "Demand of Avocado"
    elif "pricing of avocado".lower() in intent:
        intent = "Pricing of Avocado"

    elif "supply of avocado".lower() in intent:
        intent = "Supply of Avocado"

    elif "weather of us and mexico".lower() in intent:
        intent = "Weather of US and Mexico"

    elif "Holidays and Events".lower() in intent:
        intent = "Holidays and Events"

    elif "Undefined".lower() in intent:
        intent = "Undefined"

    return intent
