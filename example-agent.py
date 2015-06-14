#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Rayed Alrashed 2015-06-14

AgentX sub agent paackge

snmpwalk -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleScalars
snmptable -v 2c -c public -Ci localhost NET-SNMP-EXAMPLES-MIB::netSnmpIETFWGTable 
SNMP table: NET-SNMP-EXAMPLES-MIB::netSnmpIETFWGTable

'''

import time
import random
import pyagentx

def str_to_oid(data):
    length = len(data)
    oid_int = [str(ord(i)) for i in data]
    return str(length) + '.' + '.'.join(oid_int)


class NetSnmpTestMibScalar(pyagentx.Updater):

    def update(self):
        self.set_INTEGER('1.0', 1000)
        self.set_OCTETSTRING('3.0', 'String for NET-SNMP-EXAMPLES-MIB')


class NetSnmpTestMibTable(pyagentx.Updater):

    def update(self):
        # implement netSnmpIETFWGTable from NET-SNMP-EXAMPLES-MIB.txt
        # Number of entries in table is random to show that MIB is reset
        # on every update
        for i in range(random.randint(3, 5)):
            idx = str_to_oid('group%s' % (i+1))
            self.set_OCTETSTRING('1.1.2.' + idx, 'member 1')
            self.set_OCTETSTRING('1.1.3.' + idx, 'member 2')


class MyAgent(pyagentx.Agent):

    def setup(self):
        self.register('1.3.6.1.4.1.8072.2.1', NetSnmpTestMibScalar)
        self.register('1.3.6.1.4.1.8072.2.2', NetSnmpTestMibTable)


def main():
    pyagentx.setup_logging()
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

