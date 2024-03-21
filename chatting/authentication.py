import os

from chatting.models import ChattingUser
import requests

# 인증 서버에서 인증 받아 오는 함수,
def authenticate(token):
    headers = {'Authorization': 'Bearer ' + token}
    url = os.environ.get('USER_MANAGEMENT_URL')
    res = requests.get(url + f'api/user-management/user-api/verify/', headers=headers)
    if res.status_code == 200:
        data = res.json()
        return {
            'id': data['id'],
            'nickname': data['nickname'],
        }
    else:
        return None