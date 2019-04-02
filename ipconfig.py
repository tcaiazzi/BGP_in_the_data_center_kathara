import re 
import os
import webbrowser
from pyvis.network import Network

filepath = 'lab_unsort.conf'  
path = os.path.dirname(os.path.realpath(__file__))
files = os.listdir('.')
prefix = 0


clos_net = Network(height="100%", width="100%",bgcolor="#222222", font_color="white")
# set the physics layout of the network



initial_x_server = 200
initial_y_server = 650
initial_x_leaves = 200
initial_y_leaves = 450
initial_x_spine = 400
initial_y_spine = 0


net = {}

def list_exists(node_id, nodes):
    for node in nodes: 
        if node_id == node["id"]:
            return node  
    return None  

def set_positions(name_n, position_list):
    global initial_x_server, initial_y_server 
    global initial_x_leaves, initial_y_leaves
    global initial_x_spine, initial_y_spine
   
    
    if re.search("leaf",  name_n):
        initial_x_leaves += 150
        position_list[name_n] = (initial_x_leaves,initial_y_leaves)
    elif re.search("spine",  name_n): 
        number = int(re.split('spine0|\[|\]=.*', name_n)[1]) 
        
        if number > 2 and number % 2 == 1: 
            initial_x_spine +=  350
        else: 
            initial_x_spine += 150
        
        
        position_list[name_n] = (initial_x_spine,initial_y_spine)
    else :
        initial_x_server += 150
        position_list[name_n] = (initial_x_server,initial_y_server)
        curr_posx1,curr_posy1 = position_list[name_n]

def get_ip(): 
    global prefix
    ip1 = "10.0.0."+str(prefix+1)+"/30"
    ip2 = "10.0.0."+str(prefix+2)+"/30"
    lan = "10.0.0."+str(prefix)+"/30"
    prefix += 4
    return ip1, ip2, lan
        
def get_image(name):
    if re.search("server",  name):
        image = "file:///"+path+"/image/server.png"
    elif re.search("spine", name): 
        image = "file:///"+path+"/image/spine.png"
    elif re.search("leaf", name):
        image = "file:///"+path+"/image/leaf.png"
    return image


def ipconfig():
    for item in files:
        if item.endswith(".startup"):
            os.remove( item )

    prefix=0
    with open(filepath) as fp:  
        line1 = fp.readline().strip()
        line2 = fp.readline().strip()
        
        cnt = 2
        position_list = {}
        while line1 and line2:


            n1 = re.split('\[|\]=', line1)
            n2 = re.split('\[|\]=', line2)   
            if(n1[2]==n2[2]):
                name_n1 = n1[0]
                eth_n1 = n1[1]
                name_n2 = n2[0]
                eth_n2 = n2[1]
                ip1, ip2, lan = get_ip()
                open(name_n1+".startup", "a").write("ifconfig eth"+eth_n1+" "+ ip1 +" up\n" )
                open(name_n2+".startup", "a").write("ifconfig eth"+eth_n2+" "+ ip2 +" up\n" )
            
                node1 = list_exists(name_n1, clos_net.nodes)
                node2 = list_exists(name_n2, clos_net.nodes)
                if node1:
                    net[name_n1].append(eth_n1 + ": "+ ip1 + " to " + name_n2 + "<br>")
                    #node1["title"] += eth_n1 + ": "+ ip1 + " to " + name_n2 + "<br>"
                else: 
                    net[name_n1] = [eth_n1 + ": "+ ip1 + " to " + name_n2 + "<br>"]
                    set_positions(name_n1, position_list)
                    curr_posx1,curr_posy1 = position_list[name_n1]
                    image = get_image(name_n1)
                    clos_net.add_node(name_n1,name_n1,title=name_n1+" neighbors:<br><br>",shape="image", physics=False, x=curr_posx1, y=curr_posy1 ,image=image)                                                                                                                                                                                               

                if node2:
                    net[name_n2].append(eth_n2 + ": "+ ip2 + " to " + name_n1 + "<br>")
                    #node2["title"] += eth_n2 + ": "+ ip2 + " to " + name_n1 + "<br>"
                else: 
                    net[name_n2] = [eth_n2 + ": "+ ip2 + " to " + name_n1 + "<br>"]
                    set_positions(name_n2, position_list)
                    curr_posx2,curr_posy2 = position_list[name_n2]
                    image = get_image(name_n2)
                    clos_net.add_node(name_n2,name_n2,title=name_n2+" neighbors:<br><br>",shape="image",physics=False, x=curr_posx2, y=curr_posy2,image=image)
                
                clos_net.add_edge(name_n1,name_n2, width=(0.1), title=lan)
                
                #print("Line {}: {}".format(cnt, line1))
                line1 = fp.readline().strip()
                cnt += 1
                #print("Line {}: {}".format(cnt, line2))
                line2 = fp.readline().strip()
                cnt += 1
            else:
                print("lans don't match")
                
            
    for node in clos_net.nodes :
        net[node["id"]].sort()
        for item in net[node["id"]]: 
            node["title"] += item
        
        
    clos_net.show("clos.html")
    #webbrowser.open_new_tab("file:///"+path+"/clos.html")

