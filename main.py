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
from pyagentx.agent import Agent



class MyAgent(Agent):

    def setup(self):
        self.register('1.3.6.1.3.9999.100', self.update)
        self.register('1.3.6.1.3.9999.200', self.update2, 10)

    def update(self):
        self.append('1.0', pyagentx.TYPE_COUNTER32, 1000)
        self.append('2.0', pyagentx.TYPE_COUNTER32, 2000)
        self.append('3.0', pyagentx.TYPE_OCTETSTRING, "String for 100 MIB")

    def update2(self):
        self.append('1.0', pyagentx.TYPE_COUNTER32, int(time.time()))
        self.append('2.0', pyagentx.TYPE_COUNTER32, 2000)
        self.append('3.0', pyagentx.TYPE_OCTETSTRING, "String for 200 MIB")


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
    a = MyAgent()
    try:
        #a.debug = 0
        a.start()
    except:
        #exiting main loop'
        pass
    finally:
        # call stop to end all async registred threads
        a.stop()


if __name__=="__main__":
    main()