#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import threading
import Queue

import pyagentx

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger = logging.getLogger('pyagentx.updater')
logger.addHandler(NullHandler())


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
                logger.debug('Updating :%s' % self._oid)
                start_time = now
                self._data = {}
                self.update()
                try:
                    self._queue.put_nowait({'oid': self._oid,
                                            'data':self._data})
                except Queue.Full:
                    logger.error('Queue full')
            time.sleep(0.1)
        logger.info('Updater stopping')

    # Override this
    def update(self):
        pass

    def setCounter32(self, oid, value):
        logger.debug('Setting Counter32 %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_COUNTER32, 'value':value}

    def setOctetstring(self, oid, value):
        logger.debug('Setting Octetstring %s = %s' % (oid, value))
        self._data[oid] = {'name': oid, 'type':pyagentx.TYPE_OCTETSTRING, 'value':value}

