from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chatting/", consumers.ChattingConsumer.as_asgi()),
]