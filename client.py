#!/usr/bin/env python


"""

Rayed Alrashed  2013-10-09

AgentX sub agent library

To help debugging run snmpd in foreground debug mode:
sudo /usr/sbin/snmpd -f -Lsd  -Dagentx -Le -u snmp -g snmp -I -smux -p /var/run/snmpd.pid

snmpget -v2c -c public localhost .1.3.6.1.4.1.36985.100.1.0

"""
import sys
import socket 
import struct
from pprint import pprint

path = "/var/agentx/master"


class Agentx(object):


    def __init__(self):
        self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
        self.socket.connect(path)
        self.state = {
            'session_id':0,
            'transaction_id':0,
            'packet_id':0,
        }
        self.decode_buf = ''


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


    def encode_hdr(self, pdu_type, payload_length=0, flags=0):
        flags = flags | 0x10  # Bit 5 = all ints in NETWORK_BYTE_ORDER
        buf = struct.pack('BBBB', 1, pdu_type, flags, 0)
        buf += struct.pack('!L', self.state['session_id']) # sessionID
        buf += struct.pack('!L', self.state['transaction_id']) # transactionID
        buf += struct.pack('!L', self.state['packet_id']) # packetID
        buf += struct.pack('!L', payload_length)
        return buf


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
            print l
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
        if vtype in [type_Integer, type_Counter32, type_Gauge32, type_TimeTicks]:
            data = struct.unpack('!L', self.decode_buf[:4])
            self.decode_buf = self.decode_buf[4:]
        elif vtype in [type_Counter64]:
            data = struct.unpack('!Q', self.decode_buf[:8])
            self.decode_buf = self.decode_buf[8:]
        elif vtype in [type_ObjectIdentifier]:
            data = self.decode_oid()
        elif vtype in [type_IpAddress, type_Opaque, type_OctetString]:
            data = self.decode_octet()
        elif vtype in [type_Null, type_noSuchObject, type_noSuchInstance, type_endOfMibView]:
            # No data
            data = None
        else:
            print "Unknow Type"
        return {'type':vtype, 'name':oid, 'data':data}


    def decode_hdr(self):
        try:
            t = struct.unpack('!BBBBLLLL', self.decode_buf[:20])
            self.decode_buf = self.decode_buf[20:]
            ret = {
                'version': t[0],
                'pdu_type':t[1],
                'flags':t[2],
                'reserved':t[3],
                'session_id':t[4],
                'transaction_id':t[5],
                'packet_id':t[6],
                'payload_length':t[7],
            }
            ret['pdu_type_name'] = pdu_type_name[ret['pdu_type']]
            return ret
        except Exception, e:
            print e
            print "Invalid packing"


    def decode_res(self):
        try:
            t = struct.unpack('!LHH', self.decode_buf[:8])
            self.decode_buf = self.decode_buf[8:]
            ret = {
                'sysUpTime': t[0],
                'error':t[1],
                'index':t[2],
            }
            return ret
        except Exception, e:
            print e
            print "Invalid packing"


    # ====================================================
    # PDU functions

    def open_pdu(self):
        buf = ''
        # timeout
        buf += struct.pack('!BBBB', 5, 0, 0, 0)
        # agent OID
        buf += struct.pack('!L', 0)
        # Agent Desc
        buf += self.encode_octet('MyAgent')
        # Add header in begining
        buf = self.encode_hdr(agentx_Open_PDU, len(buf)) + buf
        return buf


    def ping_pdu(self):
        return self.encode_hdr(agentx_Ping_PDU)


    def register_pdu(self, oid, timeout=0, priority=127):
        range_subid = 0
        buf = ''
        buf += struct.pack('BBBB', timeout, priority, range_subid, 0)
        # Sub Tree
        buf += self.encode_oid(oid)
        # Add header
        buf = self.encode_hdr(agentx_Register_PDU, len(buf)) + buf
        return buf


    def decode_response_pdu(self, buf):
        self.set_decode_buf(buf)
        ret = self.decode_hdr()
        pprint(ret)
        self.state = ret
        ret = self.decode_res()
        pprint(ret)
        print 'remaining:', len(self.decode_buf)
        if len(self.decode_buf) > 4:
            print struct.unpack('!BBBB', self.decode_buf[:4])
            print struct.unpack('!L', self.decode_buf[:4])        
        for i in range(len(self.decode_buf)/4):
            pprint(self.decode_buf[i*4:(i+1)*4])
        while len(self.decode_buf):
            value = self.decode_value()
            pprint(value)


    # ====================================================
    # Util functions 

    def start(self):
        print " ==== Open PDU ===="
        buf =  self.open_pdu()
        self.socket.send(buf)
        buf = self.socket.recv(1024)
        ret = self.decode_response_pdu(buf)
        print " ==== Ping PDU ===="
        self.state['transaction_id'] += 1
        buf = self.ping_pdu()
        self.socket.send(buf)    
        buf = self.socket.recv(1024)
        ret = self.decode_response_pdu(buf)
        print " ==== Register PDU ===="
        self.state['transaction_id'] += 1
        buf = self.register_pdu('1.3.6.1.4.1.36985')
        self.socket.send(buf)    
        buf = self.socket.recv(1024)
        ret = self.decode_response_pdu(buf)

        print " ==== Waiting for PDU ===="
        buf = self.socket.recv(1024)
        self.set_decode_buf(buf)
        ret = self.decode_hdr()
        pprint(ret)
        while len(self.decode_buf):
            oid = self.decode_oid()
            print oid


if __name__=='__main__':

    a = Agentx()
    a.start()


