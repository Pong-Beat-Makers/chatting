# 인증 서버에서 인증 받아 오는 함수,
def authenticate(token):
    if True:  # TODO: 인증 성공 시
        return {  # TEST CODE
            'id': token,
            'nickname': token + "_test_id",
        }
    else:
        return None