from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from chatting import serializers
from .authentication import authenticate
from .models import ChattingUser

class BlockingView(APIView):
    def post(self, request):
        # 임시 인증
        user_data = authenticate(request.headers.get('Authorization').split()[1])
        if user_data is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.BlockingSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = ChattingUser.objects.get(nickname=user_data['nickname'])
            blocked_user = ChattingUser.objects.get(nickname=data['target_nickname'])

            # 차단 안되어 있는 경우만 추가
            if not user.blocked_users.contains(blocked_user):
                user.blocked_users.add(blocked_user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # 임시 인증
        user_data = authenticate(request.headers.get('Authorization').split()[1])
        if user_data is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = ChattingUser.objects.get(nickname=user_data['nickname'])
        target_nickname = request.GET.get('target_nickname')

        # query parameter 없을 때 - 전부 조회
        if target_nickname is None:
            serializer = serializers.BlockedUsersSerializer(user.blocked_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # query parameter 있을 때 - 한명만 조회
        else:
            data = {
                'is_blocked': False
            }
            if user.blocked_users.contains(get_object_or_404(ChattingUser, nickname=target_nickname)):
                data['is_blocked'] = True

            return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        user_data = authenticate(request.headers.get('Authorization').split()[1])
        if user_data is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.BlockingSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = ChattingUser.objects.get(nickname=user_data['nickname'])
            blocked_user = ChattingUser.objects.get(nickname=data['target_nickname'])

            # 이미 차단된 경우만 제거
            if user.blocked_users.contains(blocked_user):
                user.blocked_users.remove(blocked_user)
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

