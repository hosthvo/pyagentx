#!/usr/bin/env python


"""

Rayed Alrashed  2013-10-09

AgentX sub agent library

To help debugging run snmpd in foreground debug mode:
sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid

snmpget -v2c -c public localhost .1.3.6.1.4.1.36985.100.1.0

"""


from agentx.pdu import PDU
from agentx.agent import Agent


def main():
    a = Agent()
    a.start()


if __name__=="__main__":
    main()