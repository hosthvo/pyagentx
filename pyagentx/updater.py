#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import,
    division,
    print_function,
)

# --------------------------------------------
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger('pyagentx.updater')
logger.addHandler(NullHandler())
# --------------------------------------------

import time
import threading
try:
    import queue
except ImportError:
    import Queue as queue


import pyagentx


class Updater(threading.Thread):

    def agent_setup(self, queue, oid, freq):
        self.stop = threading.Event()
        self._queue = queue
        self._oid = oid
        self._freq = freq
        self._data = {}

    def run(self):
        start_time = 0
        while True:
            if self.stop.is_set(): break
            now = time.time()
            if now - start_time > self._freq:
                logger.info('Updating : %s (%s)' % (self.__class__.__name__, self._oid))
                start_time = now
                self._data = {}
                try:
                    self.update()
                    self._queue.put_nowait({'oid': self._oid,
                                            'data':self._data})
                except queue.Full:
                    logger.error('Queue full')
                except:
                    logger.exception('Unhandled update exception')
            time.sleep(0.1)
        logger.info('Updater stopping')

    # Override this
    def update(self):
        pass

    def set_INTEGER(self, oid, value):
        logger.debug('Setting INTEGER %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_INTEGER, 'value':value}

    def set_OCTETSTRING(self, oid, value):
        logger.debug('Setting OCTETSTRING %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_OCTETSTRING, 'value':value}

    def set_OBJECTIDENTIFIER(self, oid, value):
        logger.debug('Setting OBJECTIDENTIFIER %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_OBJECTIDENTIFIER, 'value':value}

    def set_IPADDRESS(self, oid, value):
        logger.debug('Setting IPADDRESS %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_IPADDRESS, 'value':value}

    def set_COUNTER32(self, oid, value):
        logger.debug('Setting COUNTER32 %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_COUNTER32, 'value':value}

    def set_GAUGE32(self, oid, value):
        logger.debug('Setting GAUGE32 %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_GAUGE32, 'value':value}

    def set_TIMETICKS(self, oid, value):
        logger.debug('Setting TIMETICKS %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_TIMETICKS, 'value':value}

    def set_OPAQUE(self, oid, value):
        logger.debug('Setting OPAQUE %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_OPAQUE, 'value':value}

    def set_COUNTER64(self, oid, value):
        logger.debug('Setting COUNTER64 %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_COUNTER64, 'value':value}

