# -*- coding: UTF-8 -*-'
"""
File name  : doip.py

It reassembles the payload of IP with DoIP header and UDS msg
/*******************************************************************************
**                              Revision History                              **
********************************************************************************
** Revision   Date          By            Description                         **
********************************************************************************
**                                                                            **
*******************************************************************************/
"""
import socket
import time

#EthDiag Protocol
ETHDIAG_PROTOCOL_VER = 0xcc
ETHDIAG_INVERSE_PROTOCOL_VER = 0x33
ETHDIAG_PAYLOAD_TYPE_UPPER = 0xFC
ETHDIAG_PAYLOAD_TYPE_LOWER = 0xBC

ESU_ADDRESS_UPPER = 0xA1
ESU_ADDRESS_LOWER = 0xA2

TESTER_ADDRESS_UPPER = 0x10
TESTER_ADDRESS_LOWER = 0x00

ETHDIAG_HEADER_LIST = [ETHDIAG_PROTOCOL_VER,
                       ETHDIAG_INVERSE_PROTOCOL_VER,
                       ETHDIAG_PAYLOAD_TYPE_UPPER,
                       ETHDIAG_PAYLOAD_TYPE_LOWER,
                       TESTER_ADDRESS_UPPER,
                       TESTER_ADDRESS_LOWER,
                       ESU_ADDRESS_UPPER,
                       ESU_ADDRESS_LOWER]


class IPLayer:
    def __init__(self, ip, port, logWrite):
        self.clientsocket = None
        self.logWrite = logWrite
        self.socketconnection(ip, port)
        
    def socketconnection(self, esu_ip_address, esu_diag_port):
        
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try: 
            self.clientsocket.settimeout(5)
            self.clientsocket.connect((esu_ip_address, esu_diag_port))
            time.sleep(1)
        except:
            self.logWrite ('Socket connection failed')
            self.clientsocket = None
            return
        
        
        
        
        server_ip, server_port = self.clientsocket.getpeername()
        client_ip, client_port = self.clientsocket.getsockname()
        self.logWrite ("TCP Socket is connected!")
        self.logWrite ( "    - Server IP : %s, Server Port : %s"%(server_ip, server_port))
        self.logWrite ( "    - Client IP : %s, Client Port : %s"%(client_ip, client_port))
        
        
    def TransmitIPFrame(self, uds_data):
        dlc = len(uds_data) + 4
        
        dlc_1 = (dlc & 0xf0000000) >>28
        dlc_2 = (dlc & 0x0f000000) >>24
        dlc_3 = (dlc & 0x00f00000) >>20
        dlc_4 = (dlc & 0x000f0000) >>16
        dlc_5 = (dlc & 0x0000f000) >>12
        dlc_6 = (dlc & 0x00000f00) >>8
        dlc_7 = (dlc & 0x000000f0) >>4
        dlc_8 = (dlc & 0x0000000f)
        
        dlc_string = "%x%x%x%x%x%x%x%x"%(dlc_1, dlc_2, dlc_3, dlc_4, dlc_5, dlc_6, dlc_7, dlc_8)
        
        EthDiagHeader = "cc33fcbc%s1000a1a2"%dlc_string
        
        str_uds_data = ''
        for d in uds_data:
            upper_4bit = (d & 0xf0) >>4
            lower_4bit = (d & 0x0f)
            str_uds_data += '%x%x'%(upper_4bit, lower_4bit)
         
        EthDiagHeader += str_uds_data  
        self.clientsocket.send(EthDiagHeader.decode("hex"))
        self.logWrite ( "    Transmit Data : %s"%(str_uds_data))
        self.logWrite ( "     -EthDiag Protocol Ver:%s    -EthDiag_Iverse Protocol Ver:%s    -EthDiag Payload type:%s    -EthDiag payload length:%s"%('0xcc','0x33','0xFCBC', dlc_string))
        self.logWrite ( "     -DoIP_Source Address :%s    -DoIP_Target Address:%s    -DpIP Data:%s"%('0x1000', '0xa1a2', str_uds_data))
        
        
    
    def Reassemble(self, timestamp, data):
        msggroup = []
        
        EthDiag_proto_ver = '0x%s'%data[:2]
        EthDiag_invers_proto_ver = '0x%s'%data[2:4]
        EthDiag_payload_type = '0x%s'%data[4:8]
        EthDiag_payload_len = '0x%s'%data[8:16]
        Doip_SA = '0x%s'%data[16:20]
        Doip_TA = '0x%s'%data[20:24]
        Doip_Data = '%s'%data[24:]
        
        return (timestamp, EthDiag_proto_ver, EthDiag_invers_proto_ver, EthDiag_payload_type, EthDiag_payload_len, Doip_SA, Doip_TA, Doip_Data)
        
    
    def ReceiveMessage(self):
        data = self.clientsocket.recv(4096)       
        timestamp = time.time()
        
        return self.Reassemble(timestamp, data.encode('hex'))
        
        #return data.encode('hex')
        
    def close(self):
        self.clientsocket.close()
        time.sleep(1)