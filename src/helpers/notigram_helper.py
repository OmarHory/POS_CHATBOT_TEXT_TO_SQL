import json
import requests

def get_auth_token():
    url = "https://be-staging.fdmanalytics.com/notigram/token"
    payload = {'client_id': 'databricks', 'client_secret': 'QrdXhFrKCXjdg6ao1CkJQpE42OYlEF3j'} # add to secrets
    headers = {'Authorization': f'Basic YWRtaW5AYWRtaW4ubWU6IUAjJCVeJiooKQ=='} # add to secrets

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        raise ValueError("Auth Token hasn't succeeded.")
    return response.json()

def notify_otp(notigram_payload, token):
    
    url = "https://be-staging.fdmanalytics.com/apis/notigram/notification/send/secure-email"

    payload = json.dumps(notigram_payload)

    headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json',
      'x-api-key':'AZ87-6563-XUJH-00002', # add to secrets
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    if response.status_code != 201:
        raise ValueError("Notigram hasn't succeeded.")
        
    return response


def verify_otp(payload, token):
    url = "https://be-staging.fdmanalytics.com/apis/notigram/notification/otp/verify"

    payload = json.dumps(payload)

    headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json',
      'x-api-key':'AZ87-6563-XUJH-00002', # add to secrets
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def main():
    notigram_payload = {
    "realm": 'dmfp',
    "notification_type": 'OTP',
    "template_name": 'LEX-OTP',
    "template_type": "EMAIL_OTP",
    "lang": "EN",
    "from": "noreply@freshdelmonte.com",
    "from_in_address_name": "Delmonte Lex",
    "subject": 'WhatsApp LEX OTP',
    "contact": [
        "omar@sitech.me", 
    ],
    "template_values": {},
    }

    token = get_auth_token()['access_token']
    print("token; ", token)

    
    notify_obj = notify_otp(notigram_payload, token)
    print('notify_obj: ', notify_obj.text)
    uuid = notify_obj.json()['uuid']
    
    user_otp = input('Enter OTP: ')
    payload = {'realm':"dmfp" ,'uuid': uuid, 'otp':user_otp}
    verify_obj = verify_otp(payload, token)
    print('verify_obj: ', verify_obj.text)

    if verify_obj.json()['status']:
        print('OTP Verified')
    else:
        print('OTP Not Verified')

main()