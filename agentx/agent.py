#!/usr/bin/env python


import sys
import socket
import struct
import logging
import time
from pprint import pprint 

import agentx
from agentx.pdu import PDU


logger = logging.getLogger('agentx.agent')

class Agent(object):

    def __init__(self):
        self.session_id = 0
        self.transaction_id = 0
        self.debug = 1
        # Data Related Variables
        self.register_list = []
        self.data = {}        
        self.data_idx = []
        self.ticker = -1  # increment each tick (second)

    def _connect(self):
        while 1:
            try:
                self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
                self.socket.connect(agentx.SOCKET_PATH)
                self.socket.settimeout(1)
                return
            except socket.error:
                logger.error("Failed to connect, sleeping and retrying later")
                time.sleep(2)

    def new_pdu(self, type):
        pdu = PDU(type)
        pdu.session_id = self.session_id
        pdu.transaction_id = self.transaction_id
        self.transaction_id += 1
        return pdu

    def response_pdu(self, org_pdu):
        pdu = PDU(agentx.AGENTX_RESPONSE_PDU)
        pdu.session_id = org_pdu.session_id
        pdu.transaction_id = org_pdu.transaction_id
        pdu.packet_id = org_pdu.packet_id
        return pdu

    def send_pdu(self, pdu):
        if self.debug: pdu.dump()
        self.socket.send(pdu.encode())
        
    def recv_pdu(self):
        buf = self.socket.recv(1024)
        if not buf: return None
        pdu = PDU()
        pdu.decode(buf)
        if self.debug: pdu.dump()
        return pdu


    # =========================================

    def setup(self):
        # override this to register mib
        pass

    def tick(self):
        logger.debug("tick")
        updated = False
        self.ticker += 1
        for row in self.register_list:
            if self.ticker % row['freq'] == 0:
                logger.info("Update: %s" % (row['oid']))
                updated = True
                self._base_oid = row['oid']
                row['callback']()
        if updated:
            # recalculate reverse index if data changed
            self.data_idx = sorted(self.data.keys(), key=lambda k: tuple(int(part) for part in k.split('.')))

    def register(self, oid, callback, freq=5):
        self.register_list.append({'oid':oid, 'callback':callback, 'freq': freq})

    def append(self, oid, type, value):
        oid = "%s.%s" % (self._base_oid, oid)
        self.data[oid] = {'name': oid, 'type':type, 'value':value}

    def get_next_oid(self, oid):
        if oid in self.data:
            # Exact match found
            idx = self.data_idx.index(oid)
            if idx == (len(self.data_idx)-1):
                # Last Item in MIB, No match!
                return None
            return self.data_idx[idx+1]
        else:
            # No exact match find prefix
            for tmp_oid in self.data_idx:
                if tmp_oid.startswith(oid):
                    return tmp_oid
            return None # No match!
    
    # =========================================

    def start(self):
        self.setup()
        while 1:
            try:
                self._start_network()
            except socket.error:
                logger.error("Network error, master disconnect?!")
                pass


    def _start_network(self):
        self._connect()

        logger.info("==== Open PDU ====")
        pdu = self.new_pdu(agentx.AGENTX_OPEN_PDU)
        self.send_pdu(pdu)
        pdu = self.recv_pdu()
        self.session_id = pdu.session_id

        logger.info("==== Ping PDU ====")
        pdu = self.new_pdu(agentx.AGENTX_PING_PDU)
        self.send_pdu(pdu)
        pdu = self.recv_pdu()

        logger.info("==== Register PDU ====")
        for row in self.register_list:
            logger.info("Registering: %s" % (row['oid']))
            pdu = self.new_pdu(agentx.AGENTX_REGISTER_PDU)
            pdu.oid = row['oid']
            self.send_pdu(pdu)
            pdu = self.recv_pdu()

        logger.info("==== Waiting for PDU ====")
        while 1:
            self.tick()
            try:
                request = self.recv_pdu()
            except socket.timeout:
                continue

            if not request:
                logger.error("Empty PDU, connection closed!")
                raise socket.error

            response = self.response_pdu(request)
            if request.type == agentx.AGENTX_GET_PDU:
                logger.debug("Received GET PDU")
                for rvalue in request.range_list:
                    oid = rvalue[0]
                    logger.debug("OID: %s" % (oid))
                    if oid in self.data:
                        logger.debug("OID Found")
                        response.values.append(self.data[oid])
                    else:
                        logger.debug("OID Not Found!")
                        response.values.append({'type':agentx.TYPE_NOSUCHOBJECT, 'name':rvalue[0], 'value':0})

            elif request.type == agentx.AGENTX_GETNEXT_PDU:
                logger.debug("Received GET_NEXT PDU")
                for rvalue in request.range_list:
                    oid = self.get_next_oid(rvalue[0])
                    logger.debug("GET_NEXT: %s => %s" % (rvalue[0], oid))
                    if oid:
                        response.values.append(self.data[oid])
                    else:
                        response.values.append({'type':agentx.TYPE_ENDOFMIBVIEW, 'name':rvalue[0], 'value':0})

            self.send_pdu(response)


