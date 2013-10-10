#!/usr/bin/env python


import socket
import struct
from pprint import pprint 

import agentx
from agentx.pdu import PDU


class Agent(object):


    def __init__(self):
        self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
        self.socket.connect(agentx.SOCKET_PATH)
        self.session_id = 0
        self.transaction_id = 0
        self.debug = 1

    def new_pdu(self, type):
        pdu = PDU(type)
        pdu.session_id = self.session_id
        pdu.transaction_id = self.transaction_id
        self.transaction_id += 1
        return pdu

    def send_pdu(self, pdu):
        if self.debug: pdu.dump()
        self.socket.send(pdu.encode())
        
    def recv_pdu(self):        
        buf = self.socket.recv(1024)
        pdu = PDU()
        pdu.decode(buf)
        if self.debug: pdu.dump()
        return pdu

    def start(self):
        print " ==== Open PDU ===="
        pdu = self.new_pdu(agentx.AGENTX_OPEN_PDU)
        self.send_pdu(pdu)
        pdu = self.recv_pdu()
        self.session_id = pdu.session_id

        print " ==== Ping PDU ===="
        pdu = self.new_pdu(agentx.AGENTX_PING_PDU)
        self.send_pdu(pdu)
        pdu = self.recv_pdu()

        print " ==== Register PDU ===="
        pdu = self.new_pdu(agentx.AGENTX_REGISTER_PDU)
        pdu.oid = '1.3.6.1.4.1.36985'
        self.send_pdu(pdu)
        pdu = self.recv_pdu()

        print " ==== Waiting for PDU ===="
        while 1:
            pdu = self.recv_pdu()
            if pdu.type == agentx.AGENTX_GET_PDU:
                pprint(pdu.oids)

