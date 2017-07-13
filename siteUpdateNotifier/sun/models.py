# -*- coding: utf8 -*-

from typing import List

from django.db import models
from django.utils import timezone


class Notification(models.Model):
    METHOD_CHOICES = (
        ('mail', 'mail'),
        ('jabber', 'jabber'),
    )
    method = models.CharField(max_length=8, choices=METHOD_CHOICES)
    recipient = models.CharField(max_length=1024)
    periodicity = models.PositiveIntegerField()
    url = models.URLField()
    next_refresh_time = models.DateTimeField(blank=True, default=timezone.now)
    last_snapshot = models.TextField(blank=True, default="")
    last_status_code = models.DecimalField(max_digits=3, decimal_places=0, default=200)

    def requires_refresh(self) -> bool:
        return self.next_refresh_time < timezone.now()

    def set_refreshed(self) -> None:
        self.next_refresh_time = timezone.now() + timezone.timedelta(minutes=self.periodicity)
        self.save()

    def __str__(self) -> str:
        return "'{}' for '{}' via {} (every {}m)".format(self.url, self.recipient, self.method, self.periodicity)

    @classmethod
    def get_needing_refresh(cls) -> List['Notification']:
        return cls.objects.filter(next_refresh_time__lt=timezone.now())
