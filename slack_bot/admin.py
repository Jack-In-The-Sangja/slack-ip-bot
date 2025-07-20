from django.contrib import admin
from .models import IPAccessRequest

@admin.register(IPAccessRequest)
class IPAccessRequestAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'list_type', 'type', 'device', 'requester', 'requested_at', 'expires_at')
    search_fields = ('ip_address', 'requester')
    list_filter = ('list_type', 'device', 'type')
    ordering = ('-requested_at',)
