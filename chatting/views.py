from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chatting.serializers import BlockingSerializer
from .authentication import authenticate
from .models import ChattingUser

class BlockingView(APIView):
    def post(self, request):
        serializer = BlockingSerializer(data=request.data)
        user_data = authenticate(request.headers.get('Authorization').split()[1])
        if user_data is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            data = serializer.validated_data
            user = ChattingUser.objects.get(nickname=user_data['nickname'])
            blocked_user = ChattingUser.objects.get(nickname=data['target_nickname'])

            # true 이면 차단 추가, false 이면 차단 해제
            # TODO: 이미 차단되었거나 이미 해제인 경우 에러처리
            if data['block_requested'] is True:
                user.blocked_users.add(blocked_user)
            else:
                user.blocked_users.remove(blocked_user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)