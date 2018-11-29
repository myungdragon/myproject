# -*- coding: UTF-8 -*-'
"""
File name  : DoIPTest.py
/*******************************************************************************
**                              Revision History                              **
********************************************************************************
** Revision   Date          By            Description                         **
********************************************************************************
**                                                                            **
*******************************************************************************/
"""
from DoIP import monitorjob
from threading import Timer
import time
import xml.etree.ElementTree as ET
import arxml_utility  as AU


ESU_IP_ADDRESS = '10.0.4.0'
ESU_DIAG_PORT = 13404

ESU_ADDRESS = 0xA1A2
TESTER_ADDRESS_UPPER = 0x1000


class MyApp():   

    def __init__(self):
        self.rxdispatch = {}
        self.txdispatch = {}
        
        self.trigger = None
        self.timer = None
        self.timer_started = False
        self.trace = ''
        
        self.TestStart()
        
    def TestStart(self):
        self.start_time = time.time()
        now = time.localtime()
        date = "%04d-%02d-%02d"% (now.tm_year, now.tm_mon, now.tm_mday)
        localtime = "%02d:%02d:%02d" % (now.tm_hour, now.tm_min, now.tm_sec)
        
        self.Print("\n#############################################################")
        self.Print("\n        Diagnostic Auto Test Start")
        self.Print("\n        - date : %s"%(date))
        self.Print("\n        - Time : %s"%(localtime))
        self.Print("\n#############################################################")
        
        self.LoadCfg()
        
        self.todo = 'Diag_TestSeq0'
        
        self.trigger = monitorjob.TriggerJob(ESU_IP_ADDRESS,
                                             ESU_DIAG_PORT,
                                             self.Print)
        
        if self.trigger and self.trigger.clientsocket:
            self.trigger.setMsgHandler(None, self.RxEventCallback)
            self.OnScheduleService()
        else:
            self.Print( 'Test is terminated because the socket connection failed')
        
        
    def TestClose (self):
         
        if self.trigger:
            self.trigger.close()
            
        self.Print( 'close' )
        
        #save trace
        now = time.localtime()
        date = "%04d%02d%02d_%02d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        f = open('log_%s.txt'%(date),'w')
        f.write( self.trace )
        f.close()
        
    def LoadCfg (self):
        """Load TestCase_Diag.arxml"""
        
        diag_arxml = 'TestCase_Diag_.arxml'
        doc = ET.parse(diag_arxml)
        
        self.testseq =  AU.Find_ShortnameList_By_DefinitionRef(doc, '/AUTRON/TestCase_Diag/Diag_TestSeq')
  
        for row, tc in enumerate(self.testseq):
            tx_dict = {}
            rx_dict = {}
            
            tx_dict['tx'] = self.SendDiag
            tx_dict['serviceId'] = serviceId =  int(AU.Find_EcucNumParamValue_By_ShortName(doc, tc, 'SeviceId'),16)
            tx_dict['armtime'] = True
            tx_dict['timeout']= (float(AU.Find_EcucNumParamValue_By_ShortName(doc, tc, 'TimeDelay'))/1000)
            tx_dict['funcaddr'] = False
            tx_dict['nextseq'] = tc+'_RWAIT'
            tx_dict['subfncavail'] = True if(int(AU.Find_EcucNumParamValue_By_ShortName(doc, tc, 'Sub_FunctionAvail')) ==1) else False
            try :
                tx_dict['subfnc'] = int(AU.Find_EcucNumParamValue_By_ShortName(doc, tc, 'SubFunction'), 16)
            except ValueError:
                tx_dict['subfnc'] = 0
            data = AU.Find_EcucTextParamVaueList_By_ShortName(doc, tc, 'data')
            
            data_string = self.listtostring( data)
            tx_dict['data'] = self.liststringtoint( data_string)
            tx_dict['index'] = row
            tx_dict['TestInfo'] = AU.Find_EcucTextParamValue_By_ShortName(doc, tc, 'TestInformation')
            
            self.txdispatch[tc]= tx_dict 
            
            rx_dict['rx'] = self.RcvDiag
            
            seqname = tc[:12]
            seqnum = int(tc[12:])
            if seqnum+1 == len(self.testseq):
                nextseq = 'TESTEND'
            else:
                nextseq = '%s%d'%(seqname,seqnum+1)
            rx_dict['nextseq'] = nextseq
            
            ExpectedResult = AU.Find_EcucTextParamVaueList_By_ShortName(doc, tc, 'ExpectedResult')
            rx_dict['expresult'] = self.listtostring( ExpectedResult)
            rx_dict['index'] = row
            self.rxdispatch[tc+'_RWAIT'] = rx_dict
    
    
    def liststringtoint (self, str_lst):
        data = []
        
        if str_lst == '':
            return data
        
        for str in str_lst.split(', '):
            data.append(int(str, 16))
         
        return data
    
    def SendDiag (self):
        self.Print('\n\n********************* %s Test Start **********************'%(self.todo))
        self.Print('\n Test Information : %s'%(self.txdispatch[self.todo]['TestInfo']))
        
        
        msg = []
        serviceId = self.txdispatch[ self.todo ]['serviceId']
        msg.append(serviceId)
        if self.txdispatch[ self.todo ]['subfncavail']:
            subfunction = self.txdispatch[ self.todo ]['subfnc']
            msg.append(subfunction)
            
        if self.txdispatch[ self.todo ]['data'] != []:
            msg += self.txdispatch[ self.todo ]['data']
        
        cur_time = time.time() - self.start_time
        
        
        self.Print('\n * UDS Service Request')
        self.Print('    Time : %f sec.'%(round(cur_time,3)))
        
        self.trigger.SendProtocolMsg(msg)
        
        # next sequence
        self.todo = self.txdispatch[ self.todo ]['nextseq']
        
    
    def RcvDiag (self, rxmsg):
        self.Print('\n    - %s : Test Result check'%(self.todo))
        
        exp_result = self.rxdispatch[self.todo]['expresult']
        
        # Compare Function
        result, index = self.CheckExpectedResult(rxmsg, exp_result)
        
        if result:
            self.Print('\n    - Result : Test OK')
        else:
            self.Print('\n    - Result : Test NOK')  
            
       
        self.todo = self.rxdispatch[self.todo]['nextseq']
        
    def listtostring(self, data):
        re_data = ''
        for index, val in enumerate(data):
            if index == 0:
                re_data = val
            else:
                re_data +=', %s'%(val) 
            #ExpectedResult = AU.Find_EcucTextParamVaueList_By_ShortName(doc, tc, 'ExpectedResult')
        
        return re_data
    #-------------------------------------------------------
    # Check Result
    #-------------------------------------------------------
    def CheckExpectedResult(self,rxmsg, exp_result):
        result = True
        
        rxdata = []
        expdata = []
        
        for index in range(0, len(rxmsg), 2):
            rxdata.append('0x'+rxmsg[index:index+2])
        
        index = 0
        
        for str in exp_result.split(', '):
            expdata.append(str)
           
        
        for data in expdata:
            if rxdata[index] != data:
                result = False
                break
            index+=1
            
        return result, index
    
    #--------------------------------------------------------
    # Ethernet Data process
    #--------------------------------------------------------     
        
    def RxEventCallback(self, timestamp, EthDiag_proto_ver, EthDiag_invers_proto_ver, EthDiag_payload_type, EthDiag_payload_len, Doip_SA, Doip_TA, Doip_Data):
        cur_time = timestamp - self.start_time
        self.Print('\n * UDS Service Response')
        self.Print('    Time : %f sec.'%(round(cur_time,3)))
        self.Print( "    Received Data : %s"%(Doip_Data))
        self.Print( "     -EthDiag Protocol Ver:%s    -EthDiag_Iverse Protocol Ver:%s    -EthDiag Payload type:%s    -EthDiag payload length:%s"%(EthDiag_proto_ver,EthDiag_invers_proto_ver,EthDiag_payload_type, EthDiag_payload_len))
        self.Print( "     -DoIP_Source Address :%s    -DoIP_Target Address:%s    -DpIP Data:%s"%(Doip_SA, Doip_TA, Doip_Data))
        
        self.ScheduleService(Doip_Data)
        
    #-------------------------------------------------------
    # Scheduling Service
    #-------------------------------------------------------
    def ScheduleService(self, rxmsg):
        
        if self.rxdispatch.has_key( self.todo ):
            self.rxdispatch[ self.todo ]['rx'](rxmsg)
            
            
        if self.txdispatch.has_key(self.todo):
           
            if self.txdispatch[ self.todo ]['armtime']:
                
                if not self.timer_started:
                    self.timer = Timer(self.txdispatch[ self.todo ]['timeout'], self.OnScheduleService)    
                    self.timer.start()
                    self.timer_started = True
                    
        else:
            if self.todo == 'TESTEND':
                self.Print('\n#############################################################')
                self.Print('\n: End of Test Sequence')
                
            else:
                self.Print('\nUDS: Undefined KEY todo(%s)'%(self.todo))
                
            self.TestClose()
        
    
    def OnScheduleService(self):

        if self.timer_started:
            self.timer.cancel()
            self.timer_started = False
               
        
        if self.txdispatch[ self.todo ]['funcaddr']:
            self.txdispatch[ self.todo ]['tx']()
        else:
            self.txdispatch[ self.todo ]['tx']()
 
        
    
    def Print(self, data):
        print data
        self.trace += '\n%s'%(data)
        
        
  
if __name__ == '__main__':
    app = MyApp()