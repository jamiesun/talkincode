#!/bin/bash
#
# chkconfig: - 15 85
#
# processname: uwsgi
# config: /talkincode/uwsgi.xml

# source function library
. /etc/profile

# uWSGI config
CONFIG=/talkincode/uwsgi.xml
PID=/var/run/uswgi.pid
UWSGI=/usr/bin/uwsgi
RETVAL=0

prog="uwsgi"

case "$1" in
  start)
    # Check that networking is up.
    [ "${NETWORKING}" = "no" ] && exit 1

    # The process must be configured first.
    [ -f $CONFIG ] || exit 6

    echo -n $"Starting $prog. "

    $UWSGI $CONFIG
    RETVAL=$?
    [ $RETVAL -eq 0 ] && touch /var/lock/subsys/uwsgi
    echo
    ;;
  stop)
    echo -n $"Shutting down $prog: "
    kill -9 `cat $PID` >/dev/null 2>&1
    RETVAL=$?
    [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/uwsgi
    echo
    ;;
  restart|reload)
        $0 stop
        $0 start
    RETVAL=$?
        ;;
  *)
    echo $"Usage: $0 {start|stop|restart|reload}"
    exit 2
esac

exit $RETVAL