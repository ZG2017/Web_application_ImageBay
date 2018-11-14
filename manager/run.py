from app import webapp
from flask_apscheduler import APScheduler
from app.check_func import auto_check_func

class Config(object):
    JOBS = [
        {
            'id': 'test',
            'func': '__main__:auto_check_func',
            'args': '',
            'trigger': 'interval',
            'seconds': 10,
        }
    ]


# init apscheduler
webapp.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(webapp)
scheduler.start()


# start running
webapp.run()