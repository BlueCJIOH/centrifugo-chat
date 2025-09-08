from django.contrib import admin
from .models import Room, RoomMember, Message


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'bumped_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'joined_at')
    search_fields = ('room__name', 'user')
    ordering = ('-joined_at',)
    autocomplete_fields = ('room',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'created_at', 'short_content')
    search_fields = ('room__name', 'user', 'content')
    list_filter = ('room',)
    ordering = ('-created_at',)
    autocomplete_fields = ('room',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room')

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
