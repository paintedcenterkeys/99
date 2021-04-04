from g import datanode as dn
from g.datanode import socknode as sn

from g.datanode.replnode import ReplNode


client = sn.SockNodeClient("10.0.0.85", 14517)
client.run()

printnode = dn.DataNode(print)

def con_print(x):
	temp = x.split("|")
	if temp[0] == 'i':
		pass
	elif temp[0] == 'p':
		return temp[1]
	else:
		print('Bad string identifier thingy')

def con_input(x):
	tempp = x.split("|")
	if tempp[0] == 'p':
		pass
	elif tempp[0] == 'i':
		return input(tempp[1])
	else:
		print('Bad string identifier thingy')

con_printnode = dn.DataNode(con_print)
con_inputnode = dn.DataNode(con_input)

con_printnode << client
con_inputnode << client

con_inputnode >> client
con_printnode >> printnode

import time
time.sleep(100)