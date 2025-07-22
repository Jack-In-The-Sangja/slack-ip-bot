from django.contrib import admin
from .models import IPAccessRequest, IPAccessLog
from django.contrib import messages

@admin.register(IPAccessRequest)
class IPAccessRequestAdmin(admin.ModelAdmin):
    column_list = (
        "ip_address",
        "device",
        "requester",
        "expires_at",
        "requested_at",
        "group_id",
        "from_port",
        "to_port",
        "protocol",
    )
    list_display = column_list
    list_filter = column_list
    search_fields = column_list

    actions = ["delete_selected_ips"]

    @admin.action(description="선택한 IP 접근 요청 삭제")
    def delete_selected_ips(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count}개의 IP 접근 요청을 삭제했습니다.", messages.SUCCESS)


@admin.register(IPAccessLog)
class IPAccessLogAdmin(admin.ModelAdmin):
    column_list = (
        "action",
        "ip_address",
        "device",
        "requester",
        "group_id",
        "from_port",
        "to_port",
        "protocol",
        "old_expires_at",
        "new_expires_at",
        "timestamp",
    )
    list_display = column_list
    list_filter = column_list
    search_fields = column_list
    actions = ["delete_selected_logs"]

    @admin.action(description="선택한 로그 삭제")
    def delete_selected_logs(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count}개의 로그를 삭제했습니다.", messages.SUCCESS)