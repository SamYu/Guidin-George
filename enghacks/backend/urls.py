from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.sms_response, name='api'),
]
