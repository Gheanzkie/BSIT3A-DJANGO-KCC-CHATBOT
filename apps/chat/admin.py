from django.contrib import admin

from .models import Conversation, Message, MessageReport, Notification


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'message_count', 'updated_at']
    search_fields = ['user__username', 'user__email', 'title']

    @admin.display(description='Messages')
    def message_count(self, obj):
        return obj.messages.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'engine', 'created_at']
    list_filter = ['role', 'engine']
    search_fields = ['content']


@admin.register(MessageReport)
class MessageReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'reason', 'status', 'created_at', 'replied_at']
    list_filter = ['status', 'reason']
    search_fields = ['user__username', 'user__email', 'answer_text', 'details']
    readonly_fields = ['question_text', 'answer_text', 'sources', 'engine', 'created_at', 'replied_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'kind', 'is_read', 'created_at']
    list_filter = ['is_read', 'kind']
    search_fields = ['user__username', 'user__email', 'title', 'body']

