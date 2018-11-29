# -*- coding: utf-8 -*-

import time
import monitorjob

NMNODE_ID = 0x5d 

TIME_INTV = 0.5 #500ms
CYCLE_CRITERIA = 0.01 #1% 
CYCLE_LOW_CRITERIA = TIME_INTV-(TIME_INTV *CYCLE_CRITERIA)
CYCLE_HIGH_CRITERIA = TIME_INTV+(TIME_INTV *CYCLE_CRITERIA)
TESTCNT = 100
NM_IP_ADDRESS = ''
NM_PORT_NUMBER = 13800

ERR_CODE = {1 : 'Freqeuncy Error_Low',
            2 : 'Frequency Error_High',
            3 : 'Incorrect NM Node Id'}


class MyApp():
        def __init__ (self):
		self.trigger = None
		self.sock = None

                self.oldtime = 0
                self.curtime = 0
                self.testcnt = 0
                self.errlog_list = []
		
		self.NmTestStart()
	def NmTestStart(self):
                print ('<<<<<<<<<<<<<UDP NM TEST START>>>>>>>>>>>>>>>')
                print (' Description : The NM packet should be recieved in evry 500ms')
                print (' Test Criteria')
                print ('        - The interval of received NM Msg should be between %dms and %dms'%(CYCLE_LOW_CRITERIA*1000, CYCLE_HIGH_CRITERIA*1000))
                print ('          (Inrerval Margin : %d percent)'%(CYCLE_CRITERIA*100))
                print ('        - The NM node Id should be 0x%x'%(NMNODE_ID))
        

                '''
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind(('', 13800))
                '''
                self.trigger = monitorjob.ReceiveJob(NM_IP_ADDRESS,
                                                     NM_PORT_NUMBER)
                self.trigger.start()

                if self.trigger:
                        self.trigger.setRxHandler(None, self.RxEventCallback)
                        self.trigger.setRxTimeout(self.RxTimeoutCallback)

                

        def NmTestEnd (self):
                print ('<<<<<<<<<<<<<TEST End>>>>>>>>>>>>>>>')
                print (' - Number of the monitored NM message : %d'%( TESTCNT))
                print ('<<<<<<<<<<<<<TEST End>>>>>>>>>>>>>>>')
                
                if self.trigger:
                        self.trigger.stop()
                        #self.trigger.join(1)

        def TestResultReport(self):
                print ('<<<<<<<<<<<<<TEST Result>>>>>>>>>>>>>>>')
                if self.errlog_list == []:
                        print('    - TEST OK')
                else:
                        print('    - TEST NOK')
                        for err_dict in self.errlog_list:
                                print('      No: %d Error Reason : %s, time interval:%f, data:%s'%( err_dict['No'], err_dict['Error reason'], err_dict['Interval'], err_dict['data']))
                                
	def Eval_Test(self, timeintv, data):
                err_code = 0

                #1. frequency check
                if timeintv <= CYCLE_LOW_CRITERIA:
                        err_code = 1
                        if timeintv >= CYCLE_HIGH_CRITERIA:
                                err_code =2

                #2. NM Node ID check
                node_id = int(data[:2],16)
                if node_id != NMNODE_ID:
                        err_code =3

                return err_code
                
                
        def RxTimeoutCallback(self):
                print ('<<<<<<<<<<<<<TEST End>>>>>>>>>>>>>>>')
                print 'Test was terminated because of RX time-out'
                print ('<<<<<<<<<<<<<TEST End>>>>>>>>>>>>>>>')

        def RxEventCallback(self, timestamp, src_ip, src_port, data):
                err_dict = {}
                self.curtime = timestamp
                if self.oldtime == 0:
                        print ('<<<<<<<<<<<<<Received Data>>>>>>>>>>>>>>>')
                        self.teststarttime = timestamp
                else:
                        timeintv = self.curtime - self.oldtime
                        err_code = self.Eval_Test(timeintv, data)
                        if err_code != 0:
                                err_dict['No'] = self.testcnt
                                err_dict['Error reason'] = ERR_CODE[err_code]
                                err_dict['data'] = data
                                err_dict['Interval'] = timeintv
                                self.errlog_list.append(err_dict)
                        print(' No:%d time:%f data:%s'%(self.testcnt, (timestamp - self.teststarttime),data))


                
                if self.testcnt >= TESTCNT:
                        self.TestResultReport()
                        self.NmTestEnd()
                else:
                        self.oldtime = self.curtime
                        self.testcnt += 1
                        
                        
                


if __name__ =='__main__':
        app = MyApp()
