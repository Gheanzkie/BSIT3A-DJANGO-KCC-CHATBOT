from django.contrib import admin

from .models import ActivityLog, Announcement, AnnouncementImage, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'user', 'name', 'email', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('message', 'name', 'email', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'resolved_at')


class AnnouncementImageInline(admin.TabularInline):
    model = AnnouncementImage
    extra = 1


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'message')
    inlines = [AnnouncementImageInline]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'method', 'action', 'path', 'status_code', 'ip')
    list_filter = ('method', 'status_code')
    search_fields = ('action', 'path', 'user__username', 'user__email', 'ip')
    readonly_fields = ('created_at',)
