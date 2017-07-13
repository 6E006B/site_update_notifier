#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteUpdateNotifier.settings")
import django
django.setup()

import difflib
import html2text
import requests
import sleekxmpp
import time

from sun.models import Notification

import config

class DiffResult:
    url = None
    status_code = None
    text = None

    def __init__(self, url: str):
        self.url = url

    def __str__(self) -> str:
        status_code_change = "" if not self.status_code else "Status code has changed: {}".format(self.status_code)
        text_change = "" if not self.text else "Site content has changed:\n{}".format(self.text)
        return """Update for '{}'
        {}
        {}
        """.format(self.url, status_code_change, text_change)


class SiteUpdateNotifier:

    def __init__(self):
        self.jabber_client = JabberClient(config.jabber['username'], config.jabber['password'])

    def main(self) -> None:
        try:
            while True:
                self.check_sites()
                # sleep_time = Notification.objects.order_by('periodicity').first().periodicity
                # time.sleep(sleep_time * 60)
                time.sleep(60)
        except KeyboardInterrupt:
            self.jabber_client.disconnect()
            self.jabber_client.abort()
            print("Daemon stopped by KeyboardInterrupt")

    def check_sites(self) -> None:
        print("checking")
        notifications = Notification.get_needing_refresh()
        for notification in notifications:
            diff_result = self.diff_site(notification)
            print("diff result: {}".format(diff_result))
            if diff_result.status_code or diff_result.text:
                self.notify(notification, diff_result)
            notification.set_refreshed()

    def diff_site(self, notification: Notification) -> DiffResult:
        diff_result = DiffResult(notification.url)
        response = requests.get(notification.url)
        if not str(response.status_code) == str(notification.last_status_code):
            diff_result.status_code = "{} -> {}".format(notification.last_status_code, response.status_code)
            notification.last_status_code = response.status_code
        text = html2text.html2text(response.text)
        diff = self.create_diff(notification.last_snapshot, text)
        if diff:
            diff_result.text = diff
            notification.last_snapshot = text
        if diff_result.status_code or diff_result.text:
            notification.save()
        return diff_result

    def create_diff(self, previous: str, current: str) -> str:
        diff = ""
        for line in difflib.unified_diff(previous.split("\n"), current.split("\n"), fromfile="previous", tofile="after"):
            diff += line + "\n"
        return diff

    def notify(self, notification: Notification, diff_result: DiffResult) -> None:
        if notification.method == 'jabber':
            self.send_jabber_notification(notification.recipient, diff_result)
        elif notification.method == 'mail':
            self.send_mail_notification(notification.recipient, diff_result)
        else:
            print("ERROR: Unknown notification method '{}'!".format(notification.method))

    def send_jabber_notification(self, recipient: str, diff_result: DiffResult) -> None:
        # TODO: perform the following two checks in JabberClient.send()?
        if not self.jabber_client:
            self.jabber_client = JabberClient()
        self.jabber_client.send_message(recipient, str(diff_result), mtype='chat')

    def send_mail_notification(self, recipient: str, diff_result: DiffResult) -> None:
        if not self.mail_client:
            self.mail_client = MailClient()
        self.mail_client.send_message(recipient, str(diff_result))


class JabberClient(sleekxmpp.ClientXMPP):

    def __init__(self, jid: str, password: str):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.connect()
        self.process(block=False)


class MailClient:
    pass


if __name__ == "__main__":
    sun = SiteUpdateNotifier()
    sun.main()