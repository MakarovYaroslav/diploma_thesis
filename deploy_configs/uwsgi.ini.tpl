[uwsgi]
module = wsgi

master = true
processes = 5

socket-timeout = 65
socket = {{ PROJECT_NAME }}.sock
chmod-socket = 666
vacuum = true
callable = app

die-on-term = true