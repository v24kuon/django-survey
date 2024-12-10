#!/home/gtgshare006/miniconda3/envs/myenv/bin/python
# encoding: utf-8

import sys
import os

sys.path.append("/home/gtgshare006/gtgshare006.xsrv.jp/public_html/pollapp/")
os.environ['DJANGO_SETTINGS_MODULE'] = "mysite.settings"
from wsgiref.handlers import CGIHandler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
CGIHandler().run(application)
