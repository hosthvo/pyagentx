#!/usr/bin/env python


"""

Rayed Alrashed  2013-10-09

AgentX sub agent library

To help debugging run snmpd in foreground debug mode:
sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid


snmpget  -v2c -c public localhost .1.3.6.1.3.9999.100.1.0
snmpwalk -v2c -c public localhost .1.3.6.1.3.9999

"""

import logging
import time

import pyagentx
from pyagentx.pdu import PDU
from pyagentx.updater import Updater
from pyagentx.agent import Agent


class Update(Updater):

    def update(self):
        self.setCounter32('1.0', 1000)
        self.setCounter32('2.0', 2000)
        self.setOctetstring('3.0', 'String for 100 MIB')

class Update2(Updater):

    def update(self):
        self.setCounter32('1.0', int(time.time()))
        self.setCounter32('2.0', 2000)
        self.setOctetstring('3.0', 'String for 200 MIB')


class MyAgent(Agent):

    def setup(self):
        self.register('1.3.6.1.3.9999.100', Update)
        self.register('1.3.6.1.3.9999.200', Update2, 5)


def setup_login():
    logger = logging.getLogger('pyagentx')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def main():
    setup_login()
    try:
        a = MyAgent()
        a.start()
    except Exception as e:
        print "Unhandled exception:", e
        a.stop()
    except KeyboardInterrupt:
        a.stop()

if __name__=="__main__":
    main()

