# -*- coding: utf-8 -*-
#chen
import os
import sys
import time
import signal
import subprocess
import pexpect

from relatedSpread import Daemon

class MyTestDaemon(Daemon):
    def run(self):
        signal.signal(signal.SIGUSR1, self.__postHandle)
        signal.signal(signal.SIGUSR2, self.__pullHandle)
        # subprocess.call('source /home/votance/farsight_venv/venv/bin/activate', shell=True)
        # subprocess.call('supervisord -c /etc/supervisord.conf', shell=True)
        # subprocess.call('deactivate', shell=True)
        subprocess.call('/home/votance/miniconda3/bin/python /home/votance/Projects/Farsight/main.py', shell=True)
        sys.stdout.write(sys.path[0])
        while True:
            sys.stdout.write('Daemon Alive! {}\n'.format(time.ctime()))
            sys.stdout.flush()
            time.sleep(45)

    @staticmethod
    def __postHandle(signum, frame):
    	sys.stdout.write('ccccccccc')
    	subprocess.call(['pkill', 'farsight'])
    	time.sleep(4)
    	subprocess.call('/home/votance/miniconda3/bin/python /home/votance/Projects/Farsight/main.py', shell=True)
    	sys.stdout.write('tttttttttt')

    @staticmethod
    def __pullHandle(signum, frame):
        sys.stdout.write('ccccccccc')
        os.chdir('/home/votance/Projects/Farsight')
        try:
            child = pexpect.spawn('git pull')
            child.logfile = open('/tmp/pull.log', 'wb')
            child.expect('Username.*')
            child.sendline('qqmecl')
            child.expect('Password.*')
            child.sendline('cl144225971')
            child.expect(['.*files changed.*', '.*Already.*'])
            child.sendline('right')
            sys.stdout.write('sucess sucess sucess')
            time.sleep(5)
        except pexpect.EOF:
            sys.stdout.write('eof error')
        sys.stdout.write((child.before).decode('utf-8'))
        subprocess.call(['pkill', 'farsight'])
        time.sleep(4)
        subprocess.call('/home/votance/miniconda3/bin/python /home/votance/Projects/Farsight/main.py', shell=True)

if __name__ == '__main__':
    PIDFILE = '/tmp/daemon.pid'
    LOG = '/tmp/daemon.log'
    daemon = MyTestDaemon(pidfile=PIDFILE, stdout=LOG, stderr=LOG)

    if len(sys.argv) == 1:
        print('Usage: {} [start|stop] but success already'.format(sys.argv[0]), file=sys.stderr)
        daemon.start()

    else:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
            raise SystemExit(1)
