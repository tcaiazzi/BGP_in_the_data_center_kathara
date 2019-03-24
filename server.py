import os

lab = open("lab.conf", "a")

i = 0
interfaces = ["1", "2"]
servers = ["01", "02", "03", "04"]
lans=["A","G","B", "H", "M", "S", "N", "T"]
for s in servers:
    for i in interfaces:
        lab.write("server"+s+"["+i+"]=\""+lans.pop(0)+"\"\n")
    lab.write("server"+s+"[image]=frr\n")
    lab.write("\n")