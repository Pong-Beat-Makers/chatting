from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chatting/<target_nickname>/", consumers.ChattingConsumer.as_asgi()),
]