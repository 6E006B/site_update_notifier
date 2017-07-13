from django.conf.urls import url

from .views import SiteUpdateNotifier

urlpatterns = [
    # url(r'^day/(?P<day>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', DayEventView.as_view(), name='day-events'),
    url(r'^$', SiteUpdateNotifier.as_view(), name='jabberTracker'),
]
