from rest_framework import serializers
from .models import Room, RoomMember, Message


class LastMessageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'created_at']


class RoomSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    last_message = LastMessageSerializer(read_only=True)

    def get_member_count(self, obj):
        return obj.member_count

    class Meta:
        model = Room
        fields = ['id', 'name', 'version', 'bumped_at', 'member_count', 'last_message']


class MessageRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'version', 'bumped_at']


class RoomMemberSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)

    class Meta:
        model = RoomMember
        fields = ['room', 'user']
        read_only_fields = ['room', 'user']


class RoomMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMember
        fields = ['user', 'joined_at']


class RoomCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    members = serializers.ListField(
        child=serializers.CharField(max_length=64), required=False, allow_empty=True
    )

    def validate_name(self, value):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request and getattr(request, 'user', None):
            user_id = str(request.user.pk)
            # Room name must be unique for the user (among rooms where the user is a member)
            if Room.objects.filter(name=value, memberships__user=user_id).exists():
                raise serializers.ValidationError('room with this name already exists for user')
        return value

    def create(self, validated_data):
        # Creation is handled in the view to control transactions and broadcasting.
        raise NotImplementedError


class MessageSerializer(serializers.ModelSerializer):
    room = MessageRoomSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'room', 'created_at']
        read_only_fields = ['id', 'user', 'room', 'created_at']
