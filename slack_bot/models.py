from django.db import models

class IPAccessRequest(models.Model):
    device = models.CharField(max_length=50)  # 적용 대상 기기
    ip_address = models.GenericIPAddressField()  # 요청 IP
    requester = models.CharField(max_length=100)  # 요청자 식별자
    requested_at = models.DateTimeField(auto_now_add=True)  # 요청 시간
    expires_at = models.DateTimeField()  # 만료 시간
    group_id = models.CharField(max_length=100, blank=True, null=True)
    from_port = models.IntegerField(blank=True, null=True)
    to_port = models.IntegerField(blank=True, null=True)
    protocol = models.CharField(max_length=10, blank=True, null=True)  # 'tcp', 'udp', 등

    def __str__(self):
        return f"{self.group_id} ({self.requester} {self.ip_address}:{self.from_port}-{self.to_port}/{self.protocol})"

    class Meta:
        verbose_name = "IP Access Request"
        verbose_name_plural = "IP Access Requests"
        ordering = ['-requested_at']


class IPAccessLog(models.Model):
    action = models.CharField(max_length=20)  # 'add', 'remove', 'extend'
    device = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    group_id = models.CharField(max_length=100)
    from_port = models.IntegerField()
    to_port = models.IntegerField()
    protocol = models.CharField(max_length=10, blank=True, null=True)  # 'tcp', 'udp', 등
    requester = models.CharField(max_length=100)
    old_expires_at = models.DateTimeField(null=True, blank=True)
    new_expires_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action.upper()} {self.ip_address}:{self.from_port}-{self.to_port}/{self.protocol}"

    class Meta:
        verbose_name = "IP Access Log"
        verbose_name_plural = "IP Access Logs"
        ordering = ["-timestamp"]
