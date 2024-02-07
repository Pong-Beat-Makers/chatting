from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChattingUser

class ChattingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user_data = await self.auth()
        if user_data is None:  # 인증 실패 시
            await self.close()
            return
        await self.accept()
        self.user_id = user_data['id']
        self.user_nickname = user_data['nickname']

        # DB에 최초 접속이면 추가, 기존이면 온라인 갱신 및 채널 갱신.
        await database_sync_to_async(self.update_user_status_connect)()


    async def disconnect(self, close_code):
        # DB에서 오프라인
        await database_sync_to_async(self.update_user_status_disconnect)()


    async def receive_json(self, content, **kwargs):
        # target_nickname = self.scope['url_route']['kwargs']['target_nickname']
        # target_channel = await self.getTargetChannel(target_nickname)
        pass

    # my function

    # 인증서버에서 인증 받아오는 함수,
    async def auth(self):
        headers = self.scope['headers']
        token = ""
        for i in headers:
            if i[0] == b'authorization':
                token = i[1]
                break
        token = token.decode()
        if True:  # TODO: 인증 성공 시
            return {  # TEST CODE
                'id': token,
                'nickname': token + "_test_id",
            }
        else:
            return None

    async def getTargetChannel(self, target_nickname):
        return "dummy_target_channel"
        # TODO : DB에서 target_nickname을 통해 조회

    def update_user_status_connect(self):
        query = ChattingUser.objects.filter(id=self.user_id)
        if query.count() == 0:
            ChattingUser.objects.create(id=self.user_id, nickname=self.user_nickname, channel_name=self.channel_name,
                                        is_online=True)
        else:
            user = query.first()
            user.is_online = True
            user.channel_name = self.channel_name
            user.save()

    def update_user_status_disconnect(self):
        query = ChattingUser.objects.filter(id=self.user_id)
        user = query.first()
        user.is_online = False
        user.channel_name = None
        user.save()