import requests
from django.conf import settings

API_URL = settings.PGW_API_URL
URL = settings.PGW_URL
ACCEPTOR_CODE = settings.PWG_ACCEPTOR_CODE
PASSWORD = settings.PGW_PASSWORD
CALL_BACK_URL = settings.PGW_CALL_BACK_URL


def token(amount):
    url = API_URL + '/token'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'amount': int(amount),
        'acceptorCode': ACCEPTOR_CODE,
        'password': PASSWORD,
        'callBackUrl': CALL_BACK_URL,
        'segmentName': 'Trip'
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


def verify(token):
    url = API_URL + '/verify/'+ token
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    if response.status_code == 200:
        return True
    if response.status_code == 400:
        return False
    response.raise_for_status()
    
    
def check_status(token):
    url = API_URL + '/paymentStatus'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'token': token,
        'acceptorCode': ACCEPTOR_CODE,
        'password': PASSWORD,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data'] == 'COMPLETED'
