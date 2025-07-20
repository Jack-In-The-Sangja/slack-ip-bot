from django.db import models

class IPAccessRequest(models.Model):
    list_type = models.CharField(max_length=20)  # 'whitelist' or 'blacklist'
    type = models.CharField(max_length=20)  # 요청 형식 (e.g. add, remove)
    device = models.CharField(max_length=50)  # 적용 대상 기기
    ip_address = models.GenericIPAddressField()  # 요청 IP
    requester = models.CharField(max_length=100)  # 요청자 식별자
    requested_at = models.DateTimeField(auto_now_add=True)  # 요청 시간
    expires_at = models.DateTimeField()  # 만료 시간

    def __str__(self):
        return f"[{self.list_type.upper()}] {self.type} - {self.ip_address} ({self.requester})"

    class Meta:
        verbose_name = "IP Access Request"
        verbose_name_plural = "IP Access Requests"
        ordering = ['-requested_at']
