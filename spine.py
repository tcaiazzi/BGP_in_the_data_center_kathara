import os

lab = open("lab.conf", "a")

sp1 = open("spine01.startup")

i = 0
interfaces = ["1", "2", "3", "4","31", "32"]
spines = ["01", "02"]
sp1_lans = ["E", "K", "Q", "W", "Y", "Z"]
sp2_lans = ["F", "L", "R", "X", "Y", "Z"]
ips01 = ["169.254.1.1"]
for i in interfaces: 
    lab.write("spine01["+i+"]=\""+sp1_lans.pop(0)+"\"\n")
    sp1.write("ifconfig eth"+i+" "+ ips.pop() + " up")    
lab.write("spine01[image]=frr\n")
lab.write("\n")

for i in interfaces: 
    lab.write("spine02["+i+"]=\""+sp2_lans.pop(0)+"\"\n")
lab.write("spine02[image]=frr\n\n")