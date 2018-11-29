# -*- coding: UTF-8 -*-'
"""
File name  : monitorjob.py
Description: receive messages and dispatch the corresponding callback functions
/*******************************************************************************
**                              Revision History                              **
********************************************************************************
** Revision   Date          By            Description                         **
********************************************************************************
**                                                                            **
*******************************************************************************/
"""

from threading import Thread
from threading import Lock
import doip

class TriggerJob:
    def __init__(self, esu_ip_address, esu_diag_port, logWrite):
        self.clientsocket = None
        self.logWrite = logWrite
        
        self.ipdrv = doip.IPLayer(esu_ip_address, esu_diag_port, logWrite)
        self.clientsocket = self.ipdrv.clientsocket
        
        if self.clientsocket:
            self.targetthread = MonitorJob(self.ipdrv, logWrite)
            self.targetthread.start()
            
            if self.logWrite:
                self.logWrite('\nCOM: MonitorJob Rx thread is spawned')
        
        
        
    def setMsgHandler(self, tcid, targetcallback):
        if self.targetthread:
            self.targetthread.setRxHandler( tcid, targetcallback)
    
    def SendProtocolMsg(self, msglist):
        if self.ipdrv:
            self.ipdrv.TransmitIPFrame(msglist)
            
    def close(self):
        self.stopTargetThread()
        self.socketclose()
        
    def stopTargetThread(self):
        if self.targetthread:
            self.targetthread.stopThread()
            #self.targetthread.join(1)
            self.logWrite ( "MonitorJob Target Rx thread is stopped")
            
    def socketclose(self):
        if self.ipdrv:
            self.ipdrv.close()
            self.logWrite ( "Socket is disconnected!")
    
#------------------------------------------------
# Monitor thread
#------------------------------------------------

class MonitorJob(Thread):
    def __init__ (self, doip, logWrite):
        Thread.__init__(self)
        self.threadrun = True
        self.logWrite = logWrite
        self.rxMsgHandler = {}
        self.lock = Lock()
        self.sock = doip.clientsocket
        self.doip = doip

    def setRxHandler (self, tcid, rxcallback):
        self.lock.acquire()
        self.rxMsgHandler = rxcallback
        self.lock.release()

    def invokedRxMsgHandler(self, timestamp, EthDiag_proto_ver, EthDiag_invers_proto_ver, EthDiag_payload_type, EthDiag_payload_len, Doip_SA, Doip_TA, Doip_Data):
        self.lock.acquire()
        if self.rxMsgHandler:
            self.rxMsgHandler(timestamp, EthDiag_proto_ver, EthDiag_invers_proto_ver, EthDiag_payload_type, EthDiag_payload_len, Doip_SA, Doip_TA, Doip_Data)

        self.lock.release()
    
    def stopThread(self):
        self.threadrun = False

    def processRxMsgFromIP(self):
        
        timestamp, EthDiag_proto_ver, EthDiag_invers_proto_ver, EthDiag_payload_type, EthDiag_payload_len, Doip_SA, Doip_TA, Doip_Data = self.doip.ReceiveMessage()
            
        
        self.invokedRxMsgHandler(timestamp, EthDiag_proto_ver, EthDiag_invers_proto_ver, EthDiag_payload_type, EthDiag_payload_len, Doip_SA, Doip_TA, Doip_Data)

    def run(self):
        while self.threadrun: 
            self.processRxMsgFromIP()
            
            