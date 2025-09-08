from django.urls import path

from .views import RoomListViewSet, RoomDetailViewSet, RoomSearchViewSet, \
    MessageListCreateAPIView, JoinRoomView, LeaveRoomView, RoomMembersView, RoomMemberDetailView


urlpatterns = [
    path('rooms/', RoomListViewSet.as_view({'get': 'list', 'post': 'create'}), name='room-list'),
    path('rooms/<int:pk>/', RoomDetailViewSet.as_view({'get': 'retrieve'}), name='room-detail'),
    path('search/', RoomSearchViewSet.as_view({'get': 'list'}), name='room-search'),
    path('rooms/<int:room_id>/messages/', MessageListCreateAPIView.as_view(), name='room-messages'),
    path('rooms/<int:room_id>/join/', JoinRoomView.as_view(), name='join-room'),
    path('rooms/<int:room_id>/leave/', LeaveRoomView.as_view(), name='leave-room'),
    path('rooms/<int:room_id>/members/', RoomMembersView.as_view(), name='room-members'),
    path('rooms/<int:room_id>/members/<str:user_id>/', RoomMemberDetailView.as_view(), name='room-member-detail'),
]
