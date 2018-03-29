#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import,
    division,
    print_function,
)

import pyagentx

# Updater class that set OID values
class NetSnmpPlaypen(pyagentx.Updater):
    def update(self):
        self.set_INTEGER('1.0', 1000)
        self.set_OCTETSTRING('3.0', 'String for NET-SNMP-EXAMPLES-MIB')


class MyAgent(pyagentx.Agent):
    def setup(self):
        # Register Updater class that responsd to
        # the tree under "netSnmpPlaypen": 1.3.6.1.4.1.8072.9999.9999
        self.register('1.3.6.1.4.1.8072.9999.9999', NetSnmpPlaypen)


# Main 
pyagentx.setup_logging()
try:
    a = MyAgent()
    a.start()
except Exception as e:
    print("Unhandled exception:", e)
    a.stop()
except KeyboardInterrupt:
    a.stop()
