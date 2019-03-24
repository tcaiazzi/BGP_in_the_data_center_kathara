import os

lab = open("lab.conf", "a")

i = 0
interfaces = ["1", "2", "49", "50","51", "52"]
leafs = ["01", "02", "03", "04"]
lans=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
for l in leafs:
    for i in interfaces:
        lab.write("leaf"+l+"["+i+"]=\""+lans.pop(0).upper()+"\"\n")
    lab.write("leaf"+l+"[image]=frr\n")
    lab.write("\n")
    