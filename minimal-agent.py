#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyagentx

# Updater class that set OID values    
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
        self.set_COUNTER32('10.0', 2000)

# Register Updater class that responsd to
# the tree under: 1.3.6.1.4.1.8072.9999.9999
class MyAgent(pyagentx.Agent):
    def setup(self):
        self.register('1.3.6.1.4.1.8072.9999.9999', NetSnmpTestMibScalar)

# Main 
pyagentx.setup_logging()
try:
    a = MyAgent()
    a.start()
except Exception as e:
    print "Unhandled exception:", e
    a.stop()
except KeyboardInterrupt:
    a.stop()
