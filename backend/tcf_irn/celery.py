from __future__ import annotations

import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcf_irn.settings")

app = Celery("tcf_irn")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
