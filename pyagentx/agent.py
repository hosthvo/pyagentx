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
logger = logging.getLogger('pyagentx.agent')
logger.addHandler(NullHandler())
# --------------------------------------------

import time
import inspect
try:
    import queue
except ImportError:
    import Queue as queue

import pyagentx
from pyagentx.updater import Updater
from pyagentx.network import Network



class AgentError(Exception):
    pass

class Agent(object):

    def __init__(self):
        self._updater_list = []
        self._sethandlers = {}
        self._threads = []

    def register(self, oid, class_, freq=10):
        if Updater not in inspect.getmro(class_):
            raise AgentError('Class given isn\'t an updater')
        # cleanup and test oid
        try:
            oid = oid.strip(' .')
            [int(i) for i in oid.split('.')]
        except ValueError:
            raise AgentError('OID isn\'t valid')
        self._updater_list.append({'oid':oid, 'class':class_, 'freq':freq})

    def register_set(self, oid, class_):
        if pyagentx.SetHandler not in class_.__bases__:
            raise AgentError('Class given isn\'t a SetHandler')
        # cleanup and test oid
        try:
            oid = oid.strip(' .')
            [int(i) for i in oid.split('.')]
        except ValueError:
            raise AgentError('OID isn\'t valid')
        self._sethandlers[oid] = class_()

    def setup(self):
        # Override this
        pass

    def start(self):
        update_queue = queue.Queue(maxsize=20)
        self.setup()
        # Start Updaters
        for u in self._updater_list:
            logger.debug('Starting updater [%s]' % u['oid'])
            t = u['class']()
            t.agent_setup(update_queue, u['oid'], u['freq'])
            t.start()
            self._threads.append(t)
        # Start Network
        oid_list = [u['oid'] for u in self._updater_list]
        t = Network(update_queue, oid_list, self._sethandlers)
        t.start()
        self._threads.append(t)
        # Do nothing ... just wait for someone to stop you
        while True:
            #logger.debug('Agent Sleeping ...')
            time.sleep(1)

    def stop(self):
        logger.debug('Stop threads')
        for t in self._threads:
            t.stop.set()
        logger.debug('Wait for updater')
        for t in self._threads:
            t.join()

