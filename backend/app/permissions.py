import jwt
from django.conf import settings
from rest_framework.permissions import BasePermission


class IsRoomMemberOfURLRoom(BasePermission):
    """Allow only users who are members of the room referenced in URL.

    Expects a `room_id` kwarg in the view.
    """
    message = 'forbidden'

    def has_permission(self, request, view):
        room_id = getattr(view, 'kwargs', {}).get('room_id')
        if not room_id:
            return True
        from chat.models import RoomMember  # local import to avoid circular imports
        return RoomMember.objects.filter(user=str(request.user.pk), room_id=room_id).exists()


class CreatorIncludedInMembers(BasePermission):
    """Ensure the requesting user is included in `members` when creating a room."""
    message = 'creator must be included into members'

    def has_permission(self, request, view):
        # Only enforce on POST requests intended to create a room
        if request.method != 'POST':
            return True
        members = request.data.get('members') or []
        return str(request.user.pk) in {str(m) for m in members}

