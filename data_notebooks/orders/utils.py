import os
import requests
import time
import pandas as pd

def foodics_api(method, payload={}):
    
  url = f"https://api.foodics.com/v5/{method}"
  token = os.getenv('data_access_token')
  headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  if response.status_code != 200:
        return response.text

  return response.json()


def call_foodics(method, last_page, includables=None, filter = {}, return_last_page=False, from_page=1, checkpoint_path='data/raw/pull_orders_', checkpoint_every = 3):
    
    list_responses = []
    counter = 0
    
    for page in range(from_page, last_page+1):
        print(f"page {page}")
        retries = 3
        success = False

        while not success and retries > 0:
            method_ = f'{method}?page={page}'
            try:
                if includables is not None:
                    method_ = method_ + f'&include={includables}'
                if len(filter):
                    filters = ''
                    for key, val in filter.items():
                        filters = f'&filter[{key}]={val}'
                    method_ = method_ + filters
                print(method_)

                response = foodics_api(method_)
                
                # If the request is successful, the following line will be executed
                if return_last_page:
                    return response['meta']['last_page']
                list_responses.append(response['data'])
                success = True
            except Exception as e:
                print(f"Request failed with page: {page} {str(e)}, retrying... {retries} retries left.")
                retries -= 1
                # time.sleep(70) # wait 70 seconds before retrying
        if counter == checkpoint_every and method == 'orders':
            print("Writing to path.")
            pd.DataFrame([item for sublist in list_responses for item in sublist]).to_csv(checkpoint_path + f'_{page}.csv', index=False)
            counter = 0
            list_responses = []
        

        if not success:
            print(f"Failed to retrieve data for page {page} after 3 retries.")
            continue

        counter+=1

    return list_responses