#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logger = logging.getLogger('pyagentx.sethandler')
logger.addHandler(NullHandler())
# --------------------------------------------

class SetHandlerError(Exception):
    pass

class SetHandler(object):

    def __init__(self):
        self.transactions = {}

    def network_test(self, session_id, transaction_id, data):
        tid = "%s_%s" % (session_id, transaction_id)
        if tid in self.transactions:
            del(self.transactions[tid])
        try:
            self.test(data)
            self.transactions[tid] = data
        except SetHandler as e:
            logger.error('TestSet failed')
            raise e

    def network_commit(self, session_id, transaction_id):
        tid = "%s_%s" % (session_id, transaction_id)        
        try:
            data = self.transactions[tid]
            self.commit(data)
            if tid in self.transactions:
                del(self.transactions[tid])
        except:
            logger.error('CommitSet failed')

    def network_undo(self, session_id, transaction_id):
        tid = "%s_%s" % (session_id, transaction_id)
        if tid in self.transactions:
            del(self.transactions[tid])

    def network_cleanup(self, session_id, transaction_id):
        tid = "%s_%s" % (session_id, transaction_id)
        if tid in self.transactions:
            del(self.transactions[tid])

    # User override these 
    def test(self, data):
        pass

    def commit(self, data):
        pass

