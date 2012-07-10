#!/usr/bin/python2.7
#encoding:utf-8
#
# chkconfig: - 91 35
# description: sayincode service script
#
# activate_this = '/opt/sayincode/pydev/bin/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
import sys
import os

python_exec = '/usr/bin/python2.7'
app_dir = "/talkincode"
app_script = "mainapp.py"
def start():
	os.system("cd %s && exec nohup %s %s &"%(app_dir,python_exec,app_script))

def stop():
    pass


def restart():
	stop()
	start()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            start()
        elif 'stop' == sys.argv[1]:
            stop()
        elif 'restart' == sys.argv[1]:
            restart()
        else:
            print "Unknown command"
            sys.exit(2)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)  