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

### 접속

path : /ws/chatting/

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
    "from": "<발신자 닉네임>"
}
```
