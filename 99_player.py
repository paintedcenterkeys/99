import random
from g import datanode as dn
from g.datanode import socknode as sn
from g.datanode.replnode import ReplNode
import time

client = sn.SockNodeClient("10.0.0.85", 14517)
client.run()
time.sleep(.5)



time.sleep(100)