import os

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChattingUser
from .authentication import authenticate
import datetime
import requests
from asgiref.sync import sync_to_async


class ChattingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # DB에서 오프라인
        if await self.is_auth():
            await self.update_user_status_disconnect()
            await self.broadcast_status("offline")

    async def receive_json(self, content, **kwargs):
        # 인증 확인
        if not await self.is_auth():
            if 'token' in content:
                user_data = await sync_to_async(authenticate)(content['token'])
                if user_data is None:
                    await self.close(3401)
                    return
                self.user_id = user_data['id']
                self.user_nickname = user_data['nickname']

                # DB에 최초 접속이면 추가, 기존이면 온라인 갱신 및 채널 갱신.
                await self.update_user_status_connect()
                await self.broadcast_status("online")
                await self.send_successful_login()
                return
            else:
                await self.close(3401)
                return

        # 인증 후 일반 메시지
        target_id = content['target_id']
        target_channel_name = await self.get_target_channel_by_id(target_id)
        if target_channel_name is None:
            await self.send_json(
                {
                    "type": "chat_message",
                    "error": "No User or Offline",
                    "from_id": target_id,
                }
            )
        else:
            data = {
                "type": "chat_message",
                "message": content['message'],
                "from": self.user_nickname,
                "from_id": self.user_id,
            }
            await self.channel_layer.send(target_channel_name, data)  # 대상에게 보냄
            await self.send_json(data)  # 자기자신에게도 보냄

    # my function

    async def chat_message(self, event):
        # 시간 데이터 추가
        event['time'] = str(datetime.datetime.now().isoformat())

        # 대상 id 추가
        event['to_id'] = self.user_id

        # 차단 조회 후 전송
        from_id = event['from_id']
        is_blocked = await self.is_blocked_user(from_id)
        if not is_blocked:
            await self.send_json(event)

    async def system_message(self, event):
        event['time'] = str(datetime.datetime.now().isoformat())
        event['to_id'] = self.user_id

        await self.send_json(event)

    async def send_successful_login(self):
        online_friends_list = await self.extract_online_friends()

        message = {
            "message": "You have successfully logged",
            "online_friends": online_friends_list,
            "to_id": self.user_id
        }
        await self.send_json(message)

    @database_sync_to_async
    def extract_online_friends(self):
        users: list = ChattingUser.objects.all()
        friends_list = self.friends_list
        friends_id_list = []

        for friend in friends_list:
            friends_id_list.append(friend['id'])
        online_user = []

        for user in users:
            if user.id in friends_id_list and user.is_online:
                online_user.append((user.id, user.nickname))

        return online_user


    async def send_status(self, event):
        event['time'] = str(datetime.datetime.now().isoformat())
        event['to_id'] = self.user_id

        await self.send_json(event)

    async def broadcast_status(self, online_or_offline: str):
        self.friends_list = await self.get_friends_list()
        for friend in self.friends_list:
            friend_name = friend['nickname']
            message = {
                "type": "send_status",
                "target_nickname": friend_name,
                "from": self.user_nickname,
                "from_id": self.user_id,
                "status": online_or_offline,
            }
            target_channel: ChattingUser = await database_sync_to_async(
                ChattingUser.objects.filter(nickname=friend_name).first)()
            if target_channel.is_online is True:
                await self.channel_layer.send(target_channel.channel_name, message)

    async def get_friends_list(self):
        url = os.environ.get('USER_MANAGEMENT_URL')
        res = requests.get(url + f's2sapi/user-management/friends/?id={self.user_id}')
        if res.status_code != 200:
            return None
        return res.json()

    @database_sync_to_async
    def get_target_channel_by_id(self, target_id):
        query = ChattingUser.objects.filter(id=target_id)
        if query.count() == 0:
            return None
        user = query.first()
        if not user.is_online:
            return None

        return user.channel_name

    @database_sync_to_async
    def update_user_status_connect(self):
        query = ChattingUser.objects.filter(id=self.user_id)
        if query.count() == 0:
            ChattingUser.objects.create(id=self.user_id, nickname=self.user_nickname, channel_name=self.channel_name,
                                        is_online=True)
        else:
            user = query.first()
            user.nickname = self.user_nickname
            user.is_online = True
            user.channel_name = self.channel_name
            user.save()

    @database_sync_to_async
    def update_user_status_disconnect(self):
        query = ChattingUser.objects.filter(id=self.user_id)
        user = query.first()
        user.is_online = False
        user.channel_name = None
        user.save()

    @database_sync_to_async
    def is_blocked_user(self, from_id):
        from_user = ChattingUser.objects.get(id=from_id)
        if ChattingUser.objects.get(id=self.user_id).blocked_users.contains(from_user):
            return True
        else:
            return False

    @database_sync_to_async
    def is_auth(self):
        query = ChattingUser.objects.filter(channel_name=self.channel_name)
        if query.count() == 0:
            return False
        return True
