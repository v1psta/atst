#!/usr/bin/env python

from atst.app import celery, make_app, make_config

config = make_config()
app = make_app(config)
app.app_context().push()
