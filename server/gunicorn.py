# http://gunicorn-docs.readthedocs.org/en/latest/configure.html#configuration-file
# -*-python-*-

import multiprocessing, os

os.environ['POSTGRES_DSN'] = 'user=postgres dbname=elections'

bind = "0.0.0.0:%s" % os.getenv('PORT', 5000)
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gunicorn.workers.ggevent.GeventWorker"
pidfile = "/run/gunicorn/pid"
