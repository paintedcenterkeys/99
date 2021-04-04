from g import datanode as dn
from g.datanode import socknode as sn

from g.datanode.replnode import ReplNode
import socket

import time

NUM_CLIENTS = 3

server = sn.SockNodeServer("10.0.0.85", 14517)
server.run(max_clients=NUM_CLIENTS)


data = [None,None,None]

def savedata0(msg):
	data[0] = msg
def savedata1(msg):
	data[1] = msg
def savedata2(msg):
	data[2] = msg
REMEMBERnode0 = dn.DataNode(savedata0)
REMEMBERnode1 = dn.DataNode(savedata1)
REMEMBERnode2 = dn.DataNode(savedata2)


def single_input(clientnumber,prompt):
	s = 'i|'+prompt
	server.connections[clientnumber].receive(s)
	while data[clientnumber] is None:
		time.sleep(0.01)
	d = data[clientnumber]
	data[clientnumber] = None
	return d

def async_input(prompt):
	s = 'i|'+prompt
	server.connections[0].receive(s)
	server.connections[1].receive(s)
	server.connections[2].receive(s)
	while data[0] is None or data[1] is None or data[2] is None:
		time.sleep(0.01)
	d = data[:]
	data[0] = None; data[1] = None; data[2] = None
	return d

def single_print(clientnumber,msg=''):
	s = 'p|'+msg
	server.connections[clientnumber].receive(s)

def all_print(msg=''):
	s = 'p|'+msg
	server.connections[0].receive(s)
	server.connections[1].receive(s)
	server.connections[2].receive(s)



def func():
	server.connections[0].run()
	server.connections[1].run()
	server.connections[2].run()
	REMEMBERnode0 << server.connections[0]
	REMEMBERnode1 << server.connections[1]
	REMEMBERnode2 << server.connections[2]


	var = async_input('test')
	all_print('hello')
	single_print(0,'hello1')



server.register_new_connection_callback(func, NUM_CLIENTS)


time.sleep(100)