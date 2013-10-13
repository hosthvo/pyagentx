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
        # Data Related Variables
        self.register_list = []
        self.data = {}        
        self.data_idx = []


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
        pdu = PDU()
        pdu.decode(buf)
        if self.debug: pdu.dump()
        return pdu


    # =========================================

    def setup(self):
        # override this to register mib
        pass

    def update(self):
        # override to register MIB values
        pass

    def register(self, oid):
        self.register_list.append(oid)

    def append(self, oid, type, value):
        self.data[oid] = {'name': oid, 'type':type, 'value':value}

    def prepare(self):
        self.data_idx = sorted(self.data.keys(), key=lambda k: tuple(int(part) for part in k.split('.')))

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
        self.update()
        self.prepare()

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
        for oid in self.register_list:
            print "Registering:", oid
            pdu = self.new_pdu(agentx.AGENTX_REGISTER_PDU)
            pdu.oid = oid
            self.send_pdu(pdu)
            pdu = self.recv_pdu()

        print " ==== Waiting for PDU ===="        
        while 1:
            request = self.recv_pdu()
            response = self.response_pdu(request)
            if request.type == agentx.AGENTX_GET_PDU:
                for rvalue in request.range_list:
                    oid = rvalue[0]
                    print "OID:", oid
                    if oid in self.data:
                        print "Found"
                        response.values.append(self.data[oid])
                    else:
                        print "Not found!"
                        response.values.append({'type':agentx.TYPE_NOSUCHOBJECT, 'name':rvalue[0], 'value':0})

            elif request.type == agentx.AGENTX_GETNEXT_PDU:
                for rvalue in request.range_list:
                    oid = self.get_next_oid(rvalue[0])
                    print "GET_NEXT: %s => %s" %(rvalue[0], oid)
                    if oid:
                        response.values.append(self.data[oid])
                    else:
                        response.values.append({'type':agentx.TYPE_ENDOFMIBVIEW, 'name':rvalue[0], 'value':0})

            self.send_pdu(response)


