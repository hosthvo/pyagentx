#!/usr/bin/env python




import sys
import socket 
import struct
from pprint import pprint

import agentx

class PDU(object):


    def __init__(self, type=0):
        self.type = type
        self.session_id = 0
        self.transaction_id = 0
        self.packet_id = 0
        self.decode_buf = ''
        self.state = {}

    
    def dump(self):
        name = agentx.PDU_TYPE_NAME[self.type]
        print "<pdu>"
        print "[%s: %d %d %d]" % (name, self.session_id, self.transaction_id, self.packet_id)
        if hasattr(self, 'response'):
            print self.response
        if hasattr(self, 'values'):
            print self.values
        print "</pdu>"
        #pprint(self.state)


    # ====================================================
    # encode functions

    def encode_oid(self, oid):
        oid = oid.strip()
        oid = oid.split('.')
        oid = [int(i) for i in oid]
        if len(oid)>5 and oid[:4] == [1,3,6,1]:
            # prefix
            prefix = oid[4]
            oid = oid[5:]
        else:
            # no prefix
            prefix = 0
        buf = struct.pack('BBBB', len(oid), prefix, 0, 0)
        for i in range(len(oid)):
            buf += struct.pack('!L', oid[i])
        return buf


    def encode_octet(self, octet):
        buf = struct.pack('!L', len(octet))
        buf += octet
        padding = 4 - (len(octet)%4)
        buf += chr(0)* padding
        return buf


    def encode_header(self, pdu_type, payload_length=0, flags=0):
        flags = flags | 0x10  # Bit 5 = all ints in NETWORK_BYTE_ORDER
        buf = struct.pack('BBBB', 1, pdu_type, flags, 0)
        buf += struct.pack('!L', self.session_id) # sessionID
        buf += struct.pack('!L', self.transaction_id) # transactionID
        buf += struct.pack('!L', self.packet_id) # packetID
        buf += struct.pack('!L', payload_length)
        return buf


    def encode(self):
        buf = ''
        if self.type == agentx.AGENTX_OPEN_PDU:
            # timeout
            buf += struct.pack('!BBBB', 5, 0, 0, 0)
            # agent OID
            buf += struct.pack('!L', 0)
            # Agent Desc
            buf += self.encode_octet('MyAgent')

        elif self.type == agentx.AGENTX_PING_PDU:
            # No extra data
            pass

        elif self.type == agentx.AGENTX_REGISTER_PDU:
            range_subid = 0
            timeout = 5
            priority = 127
            buf += struct.pack('BBBB', timeout, priority, range_subid, 0)
            # Sub Tree
            buf += self.encode_oid(self.oid)

        else:
            # Unsupported PDU type
            pass

        return self.encode_header(self.type, len(buf)) + buf




    # ====================================================
    # decode functions

    def set_decode_buf(self, buf):
        self.decode_buf = buf


    def decode_oid(self):
        try:
            t = struct.unpack('!BBBB', self.decode_buf[:4])
            self.decode_buf = self.decode_buf[4:]
            ret = {
                'n_subid': t[0],
                'prefix':t[1],
                'include':t[2],
                'reserved':t[3],
            }
            sub_ids = []
            if ret['prefix']:
                sub_ids = [1,3,6,1]
                sub_ids.append(ret['prefix'])
            for i in range(ret['n_subid']):
                t = struct.unpack('!L', self.decode_buf[:4])
                self.decode_buf = self.decode_buf[4:]
                sub_ids.append(t[0])
            return sub_ids
        except Exception, e:
            print e
            print "Invalid packing OID header:"
            pprint(self.decode_buf)

    
    def decode_octet(self):
        try:
            t = struct.unpack('!L', self.decode_buf[:4])
            l = t[0]
            self.decode_buf = self.decode_buf[4:]
            padding = 4 - (l%4)
            buf = self.decode_buf[:l]
            self.decode_buf = self.decode_buf[l+padding:]
            return buf
        except Exception, e:
            print e
            print "Invalid packing octet header"


    def decode_value(self):
        try:
            vtype,_ = struct.unpack('!HH', self.decode_buf[:4])
            self.decode_buf = self.decode_buf[4:]
        except Exception, e:
            print e
            print "Invalid packing value header"
        oid = self.decode_oid()
        if vtype in [agentx.TYPE_INTEGER, agentx.TYPE_COUNTER32, agentx.TYPE_GAUGE32, agentx.TYPE_TIMETICKS]:
            data = struct.unpack('!L', self.decode_buf[:4])
            self.decode_buf = self.decode_buf[4:]
        elif vtype in [agentx.TYPE_COUNTER64]:
            data = struct.unpack('!Q', self.decode_buf[:8])
            self.decode_buf = self.decode_buf[8:]
        elif vtype in [agentx.TYPE_OBJECTIDENTIFIER]:
            data = self.decode_oid()
        elif vtype in [agentx.TYPE_IPADDRESS, agentx.TYPE_OPAQUE, agentx.TYPE_OCTETSTRING]:
            data = self.decode_octet()
        elif vtype in [agentx.TYPE_NULL, agentx.TYPE_NOSUCHOBJECT, agentx.TYPE_NOSUCHINSTANCE, agentx.TYPE_ENDOFMIBVIEW]:
            # No data
            data = None
        else:
            print "Unknow Type:", vtype
        return {'type':vtype, 'name':oid, 'data':data}


    def decode_header(self):
        try:
            t = struct.unpack('!BBBBLLLL', self.decode_buf[:20])
            self.decode_buf = self.decode_buf[20:]
            ret = {
                'version': t[0],
                'pdu_type':t[1],
                'pdu_type_name':  agentx.PDU_TYPE_NAME[t[1]],
                'flags':t[2],
                'reserved':t[3],
                'session_id':t[4],
                'transaction_id':t[5],
                'packet_id':t[6],
                'payload_length':t[7],
            }
            self.state = ret
            self.type = ret['pdu_type']
            self.session_id = ret['session_id']
            self.packet_id = ret['packet_id']
            self.transaction_id = ret['transaction_id']
            return ret
        except Exception, e:
            print e
            print "Invalid packing"


    def decode(self, buf):
        self.set_decode_buf(buf)
        ret = self.decode_header()
        if ret['pdu_type'] == agentx.AGENTX_RESPONSE_PDU:
            # Decode Response Header
            t = struct.unpack('!LHH', self.decode_buf[:8])
            self.decode_buf = self.decode_buf[8:]
            self.response = {
                'sysUpTime': t[0],
                'error':t[1],
                'error_name':agentx.ERROR_NAMES[t[1]],
                'index':t[2],
            }
            # Decode VarBindList
            self.values = []
            while len(self.decode_buf):
                self.values.append(self.decode_value())

        elif ret['pdu_type'] == agentx.AGENTX_GET_PDU:
            pass

        else:
            # Unspported PDU type
            pass

