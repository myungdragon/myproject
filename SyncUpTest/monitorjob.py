from threading import Thread
from threading import Lock
import time
import socket

SOCKET_TIMEOUT = 5 #5sec

class ReceiveJob(Thread):
	def __init__ (self, ip_address, port_number):
		Thread.__init__(self)
		self.threadrun = True
		self.rxMsgHandler = {}
		self.rxTimeoutHandler = {}
		self.lock = Lock()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                self.sock.bind((ip_address, port_number))
                self.sock.settimeout(SOCKET_TIMEOUT)
		
	

	def setRxHandler (self, tcid, rxcallback):
		self.lock.acquire()
		self.rxMsgHandler = rxcallback
		self.lock.release()

	def setRxTimeout (self, rxtimeoutcallback):
                self.lock.acquire()
		self.rxTimeoutHandler = rxtimeoutcallback
		self.lock.release()

	def invokedRxMsgHandler(self, timestamp, src_ip, src_port, data):
		self.lock.acquire()
		if self.rxMsgHandler:
			self.rxMsgHandler(timestamp, src_ip, src_port, data)

		self.lock.release()

        def invokedRxTimeoutHandler (self):
                self.lock.acquire()
		if self.rxTimeoutHandler:
			self.rxTimeoutHandler()

		self.lock.release()
                
	
	def stopThread(self):
		self.threadrun = False

	def stop(self):
                self.stopThread()


	def run(self):
		
		
		while self.threadrun:
                        try:
                                data, addr = self.sock.recvfrom(1500)		
                                timestamp = time.time()
			
                                self.invokedRxMsgHandler(timestamp, addr[0], addr[1], data.encode('hex'))
			except:
                                self.invokedRxTimeoutHandler()
                                return


