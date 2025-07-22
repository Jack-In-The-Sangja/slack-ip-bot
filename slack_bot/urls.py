from django.urls import path
from .views import security_group_dashboard_view

urlpatterns = [
    path('', security_group_dashboard_view, name='security-group-dashboard'),
]