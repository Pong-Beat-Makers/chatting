from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import ChattingUser

class BlockingSerializer(serializers.Serializer):
    target_nickname = serializers.CharField()
    block_requested = serializers.BooleanField()

    def validate_target_nickname(self, value):
        if ChattingUser.objects.filter(nickname=value).exists():
            return value
        else:
            raise ValidationError("해당 닉네임이 존재하지 않습니다.")


class BlockedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChattingUser
        fields = ['nickname']
