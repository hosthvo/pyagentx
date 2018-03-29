#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import,
    division,
    print_function,
)

'''

Rayed Alrashed 2015-06-14

AgentX sub agent that implement some parts of NET-SNMP-EXAMPLES-MIB:
<http://www.net-snmp.org/docs/mibs/NET-SNMP-EXAMPLES-MIB.txt>

snmpwalk -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleScalars
snmptable -v 2c -c public -Ci localhost NET-SNMP-EXAMPLES-MIB::netSnmpIETFWGTable 

Try snmpset:
snmpset -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleInteger.0 i 10
snmpset -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleInteger.0 i 200
snmpset -v 2c -c public localhost NET-SNMP-EXAMPLES-MIB::netSnmpExampleString.0 s "Test"

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
        self.set_OBJECTIDENTIFIER('4.0', '1.2')
        self.set_IPADDRESS('5.0', '127.0.0.1')
        self.set_COUNTER32('6.0', 2000)
        self.set_GAUGE32('7.0', 2000)
        self.set_TIMETICKS('8.0', 1000000)
        self.set_OPAQUE('9.0', 'Test')
        self.set_COUNTER64('10.0', 2000)


class NetSnmpTestMibTable(pyagentx.Updater):

    def update(self):
        # implement netSnmpIETFWGTable from NET-SNMP-EXAMPLES-MIB.txt
        # Number of entries in table is random to show that MIB is reset
        # on every update
        for i in range(random.randint(3, 5)):
            idx = str_to_oid('group%s' % (i+1))
            self.set_OCTETSTRING('1.1.2.' + idx, 'member 1')
            self.set_OCTETSTRING('1.1.3.' + idx, 'member 2')


class NetSnmpIntegerSet(pyagentx.SetHandler):

    def test(self, oid, data):
        if int(data) > 100:
            raise pyagentx.SetHandlerError()

    def commit(self, oid, data):
        print("COMMIT CALLED: %s = %s" % (oid, data))


class MyAgent(pyagentx.Agent):

    def setup(self):
        self.register('1.3.6.1.4.1.8072.2.1', NetSnmpTestMibScalar)
        self.register('1.3.6.1.4.1.8072.2.2', NetSnmpTestMibTable)
        self.register_set('1.3.6.1.4.1.8072.2.1.1.0', NetSnmpIntegerSet)


def main():
    pyagentx.setup_logging()
    try:
        a = MyAgent()
        a.start()
    except Exception as e:
        print ("Unhandled exception:", e)
        a.stop()
    except KeyboardInterrupt:
        a.stop()

if __name__=="__main__":
    main()

