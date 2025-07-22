from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from .models import IPAccessRequest, IPAccessLog
from .utils import get_security_groups_data, add_inbound_rule, remove_inbound_rule

@require_http_methods(["GET", "POST"])
def security_group_dashboard_view(request):
    message = ""
    rule_error = ""
    success = False
    err = ""

    if request.method == "POST":
        action = request.POST.get("action")
        data = {
            "GroupId": request.POST.get("GroupId"),
            "IpProtocol": request.POST.get("IpProtocol"),  # protocol 정보 포함
            "FromPort": request.POST.get("FromPort"),
            "ToPort": request.POST.get("ToPort"),
            "CidrIp": request.POST.get("CidrIp"),
        }

        device = request.POST.get("device")
        requester = request.META.get("REMOTE_ADDR", "unknown")

        ip = data["CidrIp"].split('/')[0]
        from_port = int(data["FromPort"])
        to_port = int(data["ToPort"])
        protocol = data["IpProtocol"]  # protocol 변수 추가

        expires_at = None

        if action == "remove":
            success, err = remove_inbound_rule(data)
            expires_at = timezone.now()  # 즉시 만료 시간
            if success:
                # DB에서 실제 삭제 시 protocol도 필터에 포함
                IPAccessRequest.objects.filter(
                    ip_address=ip,
                    group_id=data["GroupId"],
                    from_port=from_port,
                    to_port=to_port,
                    device=device,
                    protocol=protocol,
                ).delete()

                IPAccessLog.objects.create(
                    action="remove",
                    device=device,
                    ip_address=ip,
                    requester=requester,
                    group_id=data["GroupId"],
                    from_port=from_port,
                    to_port=to_port,
                    protocol=protocol,
                    old_expires_at=None,
                    new_expires_at=expires_at,
                )
                message = "Rule removed successfully."
        else:
            try:
                hours = int(request.POST.get("expiration_hour"))
                if not (1 <= hours <= 24):
                    raise ValueError("Hour out of range")
                expires_at = timezone.now() + timedelta(hours=hours)
            except Exception:
                rule_error = "Invalid expiration hour. Must be between 1 and 24."

            if action == "add":
                success, err = add_inbound_rule(data)
                if success and expires_at:
                    obj, created = IPAccessRequest.objects.update_or_create(
                        ip_address=ip,
                        group_id=data["GroupId"],
                        from_port=from_port,
                        to_port=to_port,
                        device=device,
                        protocol=protocol,  # protocol 추가
                        defaults={
                            "requester": requester,
                            "expires_at": expires_at,
                        }
                    )
                    IPAccessLog.objects.create(
                        action="add",
                        device=device,
                        ip_address=ip,
                        requester=requester,
                        group_id=data["GroupId"],
                        from_port=from_port,
                        to_port=to_port,
                        protocol=protocol,  # protocol 추가
                        old_expires_at=None,
                        new_expires_at=expires_at,
                    )
                message = "Rule added successfully." if success else ""

            elif action == "extend":
                qs = IPAccessRequest.objects.filter(
                    ip_address=ip,
                    group_id=data["GroupId"],
                    from_port=from_port,
                    to_port=to_port,
                    device=device,
                    protocol=protocol,  # protocol 필터 추가
                ).order_by("-expires_at")

                count = qs.count()
                if count == 1 and expires_at:
                    current = qs[0]
                    try:
                        base_time = current.expires_at if current.expires_at > timezone.now() else timezone.now()
                        new_expires_at = base_time + timedelta(hours=hours)

                        old_exp = current.expires_at
                        current.expires_at = new_expires_at
                        current.save()

                        IPAccessLog.objects.create(
                            action="extend",
                            device=device,
                            ip_address=ip,
                            requester=requester,
                            group_id=data["GroupId"],
                            from_port=from_port,
                            to_port=to_port,
                            protocol=protocol,  # protocol 추가
                            old_expires_at=old_exp,
                            new_expires_at=new_expires_at,
                        )
                        success = True
                        message = "Expiration extended successfully."
                    except Exception:
                        rule_error = "Invalid expiration hour for extension."
                elif count == 0:
                    rule_error = "No matching rule found to extend."
                else:
                    rule_error = f"Multiple ({count}) matching rules found. Please check your input."

        if not success and err:
            rule_error = err

    devices = ["AWS Security Group"]
    protocols = ['tcp', 'udp']
    security_groups, fetch_error = get_security_groups_data()

    # 보안 그룹 데이터에 expires_at 남은 시간 표시를 위해 protocol 포함하여 조회
    for sg in security_groups:
        for rule in sg.get("InboundRules", []):
            for ip in rule.get("IpRanges", []):
                ip_addr = ip.get("CidrIp", "").split("/")[0]
                from_port = rule.get("FromPort")
                to_port = rule.get("ToPort")
                protocol = rule.get("IpProtocol")
                group_id = sg.get("GroupId")

                device = "AWS Security Group"

                matching_qs = IPAccessRequest.objects.filter(
                    ip_address=ip_addr,
                    from_port=from_port,
                    to_port=to_port,
                    group_id=group_id,
                    device=device,
                    protocol=protocol,
                ).order_by("-expires_at")

                count = matching_qs.count()

                if count == 1:
                    req = matching_qs[0]
                    if req.expires_at > timezone.now():
                        remaining = req.expires_at - timezone.now()
                        total_seconds = int(remaining.total_seconds())

                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60

                        ip["remaining"] = f"~ {hours}시간 {minutes}분 남음"
                    else:
                        ip["remaining"] = "만료됨"
                elif count == 0:
                    ip["remaining"] = None
                else:
                    ip["remaining"] = "중복됨"

    return render(request, "security_group_dashboard.html", {
        "security_groups": security_groups,
        "devices": devices,
        "protocols": protocols,
        "error": fetch_error,
        "message": message,
        "rule_error": rule_error,
    })
