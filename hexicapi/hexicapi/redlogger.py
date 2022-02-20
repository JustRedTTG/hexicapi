from hexicapi.verinfo import *
import os
i = 0
loc=""
inf=""
if not os.path.exists(loc+"logs"):
  os.mkdir(loc+"logs")
while True:
  if not os.path.exists(loc+"logs/log_"+str(i)+".txt"):
    inf=loc+"logs/log_"+str(i)+".txt"
    open(inf,"a").close()
    break
  else:
    i+=1
def log(msg):
  f = open(inf,"a+")
  f.write(msg+"\n")
  f.close()