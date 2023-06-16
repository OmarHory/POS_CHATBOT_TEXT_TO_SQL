import requests
import time
import pandas as pd


def foodics_api(resource, token, payload={}):
    url = f"https://api.foodics.com/v5/{resource}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        print(f"Request failed with {str(e)}")
        return None

    if response.status_code != 200:
        return response.text

    return response.json()


def call_foodics(
    resource,
    last_page,
    client_id,
    token,
    includables=None,
    filter={},
    return_last_page=False,
    from_page=1,
    checkpoint_every=4,
):
    # check if token is not null
    if token is None:
        raise Exception("Token is null. Please provide a valid token.")

    list_responses = []
    counter = 0

    for page in range(from_page, last_page + 1):
        print(f"page {page}")
        retries = 3
        success = False

        while not success and retries > 0:
            method_ = f"{resource}?page={page}"
            try:
                if includables is not None:
                    method_ = method_ + f"&include={includables}"
                if len(filter):
                    filters = ""
                    for key, val in filter.items():
                        filters = f"&filter[{key}]={val}"
                    method_ = method_ + filters
                print(method_)

                response = foodics_api(method_, token)

                # If the request is successful, the following line will be executed
                if return_last_page:
                    return response["meta"]["last_page"]
                list_responses.append(response["data"])
                success = True
            except Exception as e:
                print(
                    f"Request failed with page: {page} {str(e)}, retrying... {retries} retries left."
                )
                retries -= 1
                time.sleep(70)  # wait 70 seconds before retrying
        if counter == checkpoint_every and resource == "orders":
            checkpoint_path = f"data/{client_id}/raw/partitions/pull_orders_{page}.csv"
            print("Writing to path.")
            df = pd.DataFrame(
                [item for sublist in list_responses for item in sublist]
            )
            df.to_csv(checkpoint_path, index=False)
            counter = 0
            list_responses = []

        if not success:
            print(f"Failed to retrieve data for page {page} after 3 retries.")
            continue

        counter += 1

    return list_responses


import re


def generate_slug(string):
    # Replace Arabic diacritics with empty string
    slug = re.sub(r"[\u064b-\u0652]", "", string)

    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")

    # Remove any non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-zA-Z0-9-\u0621-\u064a]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading and trailing hyphens
    slug = slug.strip("-")

    # Convert string to lowercase
    slug = slug.lower()

    return slug
