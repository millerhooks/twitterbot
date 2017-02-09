#!/bin/sh

/usr/local/bin/gunicorn passenger_wsgi -w 1 -b 0.0.0.0:5000 --chdir=/home/django --log-level=DEBUG --log-file -