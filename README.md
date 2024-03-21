# chatting
drf + channels 를 이용한 실시간 채팅 서버

---
## 환경

- Python 3.11
    - 언어
- Django 5.0.1
    - 백엔드 서버
- Channels 4.0.0
    - HTTP 뿐만 아니라 Websocket, chatbot 등 다양한 프로토콜 지원하는 비동기 처리 패키지
- Daphne 4.0.0
    - ASGI(비동기 서버) application server 패키지
---

## 실행 방법
- python 3.11 환경에서 실행 가정

```shell
pip install -r requirements.txt
python manage.py makemigrations chatting
python manage.py migrate chatting
python manage.py runserver
```
---
## API Specification

## 채팅 웹소켓
### 접속

path : /ws/chatting/ <br>

### 인증

path : /ws/chatting/ (동일)

형식 : json

설명 : 최초 접속 후 token 정보 전송하여 인증
```json
{
  "token" : "<JWT token>"
}
```

응답

형식 : json

설명 : 온라인 상태의 유저 닉네임 제공
```json
{
    "message": "You have successfully logged",
    "online_friends": [
        ["<user_id1>","<user_nickname1>"],
        ["<user_id2>","<user_nickname2>"]
    ]
}
```



### 메시지 전송

path : /ws/chatting/ (동일)

형식 : json

```json
{
    "target_nickname" : "<대상 닉네임>",
    "message" : "<메시지 내용>"
}
```
## 메시지 응답

```json
{
    "type": "chat_message",
    "message": "<메시지 내용>",
    "from": "<발신자 닉네임>",
    "time": "%H:%M"
}
```
#### 해당 유저가 존재하지 않거나 오프라인일 때
```json
{
    "type": "chat_message",
    "error": "No User or Offline",
    "from": "<target_nickname>",
    "time": "%H:%M"
}
```


---

## 채팅 rest api

----
### 차단 목록 추가

path : /api/chatting/blockedusers/ <br>
method : post <br>
authentication : bearer token

```json
{
    "target_nickname" : "<차단하고자 하는 유저 닉네임 : string, 필수>"
}
```

### 응답 예시

#### 성공
status : 201 created
```json
{
    "target_nickname": "1002_test_id",
    "block_requested": true
}
```

#### 인증 실패
status : 401 UNAUTHORIZED


#### 차단할 유저 정보 없음

```json
{
    "target_nickname": [
        "해당 닉네임이 존재하지 않습니다."
    ]
}
```
----
### 차단 해제 

path : /api/chatting/blockedusers/ <br>
method : delete <br>
authentication : bearer token

```json
{
    "target_nickname" : "<차단하고자 하는 유저 닉네임 : string, 필수>"
}
```

### 응답 예시

#### 성공
status : 200 OK

#### 인증 실패
status : 401 UNAUTHORIZED

---
### 차단 목록 조회
---
#### 전부 조회
path: /api/chatting/blockedusers/ <br>
method : GET

응답: json list

```json
[
    {
        "nickname": "<차단된 유저 닉네임>"
    },
    //...
]
```
---
#### 한 유저만 조회
path: /blockedusers/?target_nickname=<차단 조회할 유저 닉네임> <br>
method : GET

응답: json <br>

status : 200 OK
```json
{
    "is_blocked": <차단인지 아닌지 : boolean>
}
```

status : 404 NOT FOUND <br>
해당 유저 닉네임이 없을 때
```json
{
    "detail": "Not found."
}
```

---
### 시스템 메시지

path : /s2sapi/system-message/   
method : POST   
body : json
description : 외부에서 요청이 아닌 시스템 내부에서 요청

```json
{
  "target_nickname": "<전송하고자 하는 유저 닉네임>",
  "message": "<메시지 내용>"
}
```
   
응답 : json

status : 200 OK
```json
{
    "type": "system_message",
    "from": "admin",
    "message": "<메시지 내용>",
    "time": "<%H:%M>"
}
```

status : 400 Bad Request   
description : 전송 형식 오류

status : 404 Not Found
description : 해당하는 유저가 없거나 오프라인일 때

---

### 실시간 친구 온라인 상태 확인

응답 : json

설명 : 새로 접속한 친구는 online 보냄, 접속 종료한 친구는 offline
```json
{
    "type": "send_status",
    "target_nickname": "<본인 닉네임>",
    "from": "<상태 업데이트 된 유저 닉네임>",
    "from_id": "<상태 업데이트 된 유저 id>",
    "status": "<online or offline>",
    "time": "<%H:%M>"
}
```