# site_update_notifier
Tool to get notified if a website changes (currently only Jabber notifications implemented).

Management of notifications is currently only available via the Django admin interface (or by directly editing the SQL database).

For the Jabber notifications valid Jabber account credentials have to be specified in the [siteUpdateNotifier/config.py](siteUpdateNotifier/config.py) file.

In order to actually receive notification SiteUpdateNotifier.py has to be running.
