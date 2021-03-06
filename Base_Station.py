#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import thread
import threading
import time
import random
import socket
from MsgHandler import MsgHandler

# photoresistor


global timerSendMsg
global buffMsg, recvMsg
global buffSize, BS_addr, BS_port   

BS_addr = '192.168.1.106'
BS_port = 23333

PORT=10086

COMMUNICATION_TIMEOUT=30

class Base_Station():
    def __init__(self):
        #initialization of all the base parameters

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        self.addr = s.getsockname()[0]
        s.close()
        #!!!!!!!!!!!!!!!!!!!!!!!!!!# Add port!!!!!!!!################################ [addr, port, energy, coor]
        #self.clusterHead=["192.168.1.172", 500, [23,35]] #[address, energy, coordinate]
        self.clusterHead=[]   #for ordinary node but a list of all nodes for the cluster head
        self.network = [] # a list of [(nodeAddr, nodePort),...]
        #self.network.append((self.addr,self.energy,self.coordinate))
        self.HasInit=False
        
    
    def send(self, addr_des, port_des, msg):
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (addr_des, port_des)
        try:
            s.sendto(msg, addr)
            print ' '
            print 'sent: ' + msg + ' to ' + addr_des
            print ' '
        except:
            code=1
        finally:
            #time.sleep(3)
            s.close()
            
        # send msg from addr_source to addr_des
        
        # return action status code:
        # 0: success
        # 1: fail
        return code
    
    
    def receive(self,addr_source, port_source):
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.bind((addr_source, port_source)) 
	s.setblocking(0)
        msgHandler=MsgHandler()
        #a=time.time() 
        #time.sleep(5)
        #b=time.time()
        #print b-a
        lastSend=time.time()
	start_time=lastSend
        number_node_activated=0
        while True:
		try:
		    #time.sleep(1)
		    #print str(time.time()-lastSend)
		    if (time.time()-lastSend)>COMMUNICATION_TIMEOUT and self.HasInit==True and lastSend!=start_time:
			print 'lost connection with cluster head for : ' + str(time.time()-lastSend)
		        self.Change_to_spare_CH()
			print 'change to spare cluster head: '+ str(self.clusterHead)
		        msg=msgHandler.Encode_CH_Change_Msg(self.clusterHead[0],self.clusterHead[1],self.clusterHead[2])
		        for eachNode in self.network:
		            code=self.send(eachNode[0], PORT, msg)
			lastSend=time.time()
                        print 'Reset lastSend time: '  +str (lastSend)
		    data, addr = s.recvfrom(1024)
		    
		    #print 'received' + data
		    type_msg=msgHandler.Decode(data)
		    if type_msg==1:
		        temp,code=msgHandler.Decode_CH_Change_Msg(data)
		        if code==0:
		            self.clusterHead=temp
		            self.RefreshNetwork(temp)
		            print '******************************'
		            print 'received: ' + str(temp)
		            print 'CH changed:'
		            print self.clusterHead
		        else:
		            print "error in decoding CH change msg."
		    elif type_msg==2:
		        temp,code=msgHandler.Decode_List_Info_Msg(data)
		        if code==0:
		            self.network=temp
			        self.clusterHead=temp[0]
                    lastSend=time.time()
		            print 'Received network info: '
                    print str(self.network)
                    print ' '
		        else:
		            print "Error in decoding list of info msg"
		    elif type_msg==3:
		        temp,code=msgHandler.Decode_Info_Msg(data)
		        if code==0 and self.HasInit==False:
		            Ischanged=self.RefreshNetwork(temp)
		            print '******************************'
		            #print 'received: '
		            #print temp
		            print 'Current Network: '
                    print str(self.network)
		            number_node_activated+=1
		            print 'Number of node activated: '+str(number_node_activated)
		            if number_node_activated>=2:
		                self.InitCH()
		                msg=msgHandler.Encode_CH_Change_Msg(self.clusterHead[0],self.clusterHead[1],self.clusterHead[2])
		                for eachNode in self.network:
		                    code=self.send(eachNode[0], PORT, msg)
		                number_node_activated=0
		                #self.clusterHead=CH
		                self.HasInit=True
			if code==0 and self.HasInit==True:
                                lastSend=time.time()
                                print 'Reset last connect time: '  + str (lastSend)
		        if code==1:
		            print 'Error in decoding info msg'
		    elif type_msg==4:
		        temp,code=msgHandler.Decode_Sensor_Data(data)
                        
		        if code==0:
                            print 'Time since last connection: '+ str(time.time()-lastSend)
		            lastSend=time.time()
                            print 'Reset last connection time: '  +str (lastSend)
		        else:
		            print 'Error in decoding sensor data' 
		    elif type_msg==5:
		        pass
		    elif type_msg==0:
		        print 'Error in decode message' + data
		except:
			pass
        #analyze data
        # connect to the speicified address and port
        # receive message
        # analyze message
        # store important information into the msg

        # return action status code
        # 0: success
        # 1: fail
        return code

    
    def InitCH(self):
        index=random.randint(0,len(self.network)-1)
        self.clusterHead=self.network[index]


    def Change_to_spare_CH(self):
        print 'Change to spare CH:'
        print 'Network before remove lost cluster head: '
        print str(self.network)
        #print str(self.clusterHead)
        code=0
	if 1==1:
	    if self.network[0][0]==self.clusterHead[0]:
                self.network.pop(0)
            else:
                self.network.pop(1)
	    # network.pop(remove_index)
	    print 'Network after remove lost node: '
        print str(self.network)   
        print 'New CH: '          
	    self.clusterHead=self.network[0]
        print ' '
        '''try:

        except:
            code=1
            print 'change error'  '''
        return code


    def RefreshNetwork(self,info):
        code=0
        print '----------------------------'
        print(info)
        address=info[0]
        energy_level=info[1]
        coor=[0,0]
        coor=info[2]
        IsChange=False
        #try:
        for i in range(len(self.network)):
            if self.network[i][0]== address:
                self.network[i][1]=energy_level
                self.network[i][2]=coor
                IsChange=True
                break

        if IsChange==False:
            self.network.append(info)
        #except :
            #print 'info updata failed.'
            #code=1

        # return action status code
        # 0: success
        # 1: fail
        return code

        


    def broadcast(self):
        code=0
        try:
            # used by cluster head 
            # broadcast msg to all the neighboring nodes to call for the energy info...
            # return action status code (success or not)
            broadcast = '<broadcast>'
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_addr = (broadcast, PORT)
            #myname = socket.getfqdn(socket.gethostname())
            #myaddr = socket.gethostbyname(myname)
            
            demand_msg='Demand_info;'+self.addr+';'
            print demand_msg
            s.sendto(demand_msg, broadcast_addr)
            s.close()
        
            self.energyDissipated('','',flag=1)
        except:
            code=1
        return code

        
    def selectNextHead(self):
        #TBC
        code=0
        try:
            self.network.sort(key= lambda x : x[1], reverse=True)
            self.clusterHead=self.network[0]
        except:
            code=1
        return code
    
    
if __name__ == '__main__':
    buff = []
    BS = Base_Station()
    #timerSendMsg = threading.Timer()
    #buffSize = 10 # for the cluster head
    beginTime = time.time()
    timerUpdateHead = time.time()
    lastSend = time.time()
    CH_start = 0 # 1: Yes ;  0: No
    HOST=''
    try:
        thread.start_new_thread(BS.receive,(HOST,BS_port,))
    except:
        print 'Thread Create Failed.'
    MS_Handler=MsgHandler()
    while (1):
        pass
        # judge if current node is cluster node
        '''if (node.clusterHead[0] == node.addr):
            if not CH_start:
                CH_start = 1
                timerUpdateHead = time.time()
                lastSend = time.time()
            
            # receive the fake data from sensor
            if (node.allSensorData!=""):
                buff.append(node.allSensorData)
                node.allSensorData = ""
            #for nodeInfo in node.network:

                #recvmsg = ''
                #node.receive(nodeInfo[0], nodeInfo[1]) # collect all the info from neighboring nodes
                #if (recvmsg!=''):
                #    buff.append(recvmsg)
            
            timeBetweenLast = time.time() - lastSend
            if (timeBetweenLast > 20):
                sendMsg = ''
                for i in range(0, len(buff)):
                    sendMsg += '\t'+ buff[i]

                node.send(BS_addr, BS_port, sendMsg)
                lastSend = time.time()
                buff = []


            duree = time.time() - timerUpdateHead
            # change cluster head
            if (duree > 10):
                print "Find next clusterhead"
                node.broadcast()
                time.sleep(1)
                print "Broadcast end"
                print "Before change: " + str(node.clusterHead[0])
                print node.network
                node.selectNextHead()
                print "Select end"
                print "After change: " + str(node.clusterHead[0])
                print node.network
                
                # tell the BS the information of the network
                node.send(BS_addr, BS_port, MS_Handler.Encode_List_Info_Msg(node.network))
                # send information to the new cluster head to let him be the new cluster head
                for eachNode in node.network:

                    code=node.send(eachNode[0], PORT, MS_Handler.Encode_CH_Change_Msg(node.clusterHead[0],node.clusterHead[1],node.clusterHead[2]))
                    print '++++++++++++++++'
                    print code
                #timerUpdateHead=
                CH_start=0
        
            
            
            #elif (len(buff)==buffSize):
            #    node.send(BS_addr, BS_port, buff)
            #    lastSend = time.time()
            
           
            
            timerUpdateHead = threading.Timer(100, node.selectNextHead)
            timerSendBS = threading.Timer(
                    20, node.send, 
                    args=[BS_addr, BS_port, msg])
            timerUpdateHead.start()
            timerSendBS.start()
            
                
        else:
            CH_start = 0

            nodeTime = time.time() - lastSend
            if nodeTime > node.period: 
                temperature = random.randint(20,25)
                sensorData = str(temperature)
                sensorData=MS_Handler.Encode_Sensor_Data(sensorData)
                node.send(node.clusterHead[0], PORT, sensorData)
                lastSend = time.time()'''         
                   
