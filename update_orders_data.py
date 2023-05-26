import pandas as pd
import requests
import json


def foodics_api(method, args={}):
    if len(args.keys()):
        if 'business_date_after' in args.keys():
            business_date_after = args['business_date_after']
            url = f"https://api.foodics.com/v5/{method}?filter[business_date_after]={business_date_after}"
    else:
        url = f"https://api.foodics.com/v5/{method}"

    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImM1ZmIxMjE2MDk0YTEyODQ3ZTkyMTBhNDAxNjUzNDE4ZDI2ZWEyZGY1YTMzYzQ2ZDcyMzM3ZDhlMTc2ZDQwMmJkNjVkNTFiNmQ4YThlYTE3In0.eyJhdWQiOiI5OTNjNWM1Ni05YjkyLTRhYmMtOWUwNy05YjdjMGNiMzQ0NzUiLCJqdGkiOiJjNWZiMTIxNjA5NGExMjg0N2U5MjEwYTQwMTY1MzQxOGQyNmVhMmRmNWEzM2M0NmQ3MjMzN2Q4ZTE3NmQ0MDJiZDY1ZDUxYjZkOGE4ZWExNyIsImlhdCI6MTY4NDk0MDU3OSwibmJmIjoxNjg0OTQwNTc5LCJleHAiOjE4NDI3OTMzNzksInN1YiI6Ijk3NWIzY2U3LTIyMTItNDZjMS1hMjg2LTA4NjU4YjQ1NWRiNSIsInNjb3BlcyI6W10sImJ1c2luZXNzIjoiOTc1YjNjZTctMzllZC00MGIxLWJmODItYmZhZjRkYmY0YTdlIiwicmVmZXJlbmNlIjoiNjMyMzc4In0.aMxoYSkN1NFxvEgfd0itmmvENYt73A7gky5AIup7rgRIe8uY5T9sJPVzOj3kJfFcCadNwBjB-h6fKMKAc1QmcJY1G5j8Va9edCUYXmUNl1hMh2OydMH87AFJ7DSqK2Wic-spanliG7tsRdLihN9aRl4676TriA8Bd93iV9J4ZPgfmhdhytE5VMNqVDDTjX2CRNo2HzJQwEQFzZjZCZwt36jSjt_zk36YGNx2Fd1zk2ryZvfDsnnSZB4G8DNJPNmd9gAfvoSW3RvYn46qXm3ZRO4dZoUaixO7Fqb1-p0_UHHTDKIHV50i4Wpc1hNCjdRGI6g1dVG8cl-sYIKa8cNKHn_PzBRy6Q81XIEMrnSLQUHxLlqDms4f4YDIAUVSfem0gKtR2UMIeS8X1FtJkgTvbXTipvoXDMilWWo0sNAJ3wSQ_75b0aPd_p_6Hbydh2-2gJilLZ6tsDbkjsx5FjUp9LNDTuWof5U-5x-1glQAixoQPcqz-LMB6pFFPq-kaecmSPOhKM24MMg2YFBTyzARjah36lZ8YtJCZ0A4N87pDsOzTI8HGyBH19Z-MtFuQpoAVoBgDG9kApCgeEjnIuJtmrEWdcyWPx0WjXqm7qGot-fRQ71IhDJT8EQ5YRiYm8Gg3Yn3AobpwhBtWRaNiVDBCxIQJMUQrQL40YCWYQxwZy4'
    headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data={})
    if response.status_code != 200:
        return response.status_code

    return response.json()


response = foodics_api('orders', {'business_date_after': '2023-05-23'})
last_page = response['meta']['last_page']
print(last_page)

import time

list_responses = []

for page in range(1, last_page+1):
    print(f"page {page}")
    retries = 3
    success = False

    while not success and retries > 0:
        try:
            response = foodics_api('orders?filter[business_date_after]=2023-05-24&page={}'.format(page))
            
            # If the request is successful, the following line will be executed
            list_responses.append(response['data'])
            success = True
        except Exception as e:
            print(f"Request failed with page: {page} {str(e)}, retrying... {retries} retries left.")
            retries -= 1
            time.sleep(70) # wait 70 seconds before retrying


    if not success:
        print(f"Failed to retrieve data for page {page} after 3 retries.")
        break

dataframe = pd.DataFrame([observation for sublist in list_responses for observation in sublist])

print("shape:", dataframe.shape)

print("Max date:", dataframe['created_at'].max())
print("Min date:", dataframe['created_at'].min())

dataframe.to_csv('data/raw/orders_updates.csv', index=False)
