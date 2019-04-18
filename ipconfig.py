import re 
import os
import webbrowser
from pyvis.network import Network
import build_net

filepath = 'lab_unsort.conf'  
path = os.path.dirname(os.path.realpath(__file__))
files = os.listdir('.')

prefix = 0
prefix1 = 0

clos_net = Network(height="100%", width="100%",bgcolor="#222222", font_color="white")

net = {}
positions_list = {}
# set the physics layout of the network


# inital positions for the nodes of the graph 
initial_x_tor = 200
initial_y_tor = 650
initial_x_leaves = 200
initial_y_leaves = 450
initial_x_spine = 350
initial_y_spine = 200
initial_x_exit = initial_x_spine
initial_y_exit = 0
initial_x_server = initial_x_tor +150
initial_y_server =  initial_y_tor 
server_y = initial_y_server

num_server_per_tor =  build_net.num_server_per_tor
num_tor = build_net.num_tor


def list_exists(node_id, nodes):
    for node in nodes: 
        if node_id == node["id"]:
            return node  
    return None  

# set the positions of the node (name_n) and puts it in positions_list
def set_positions(name_n, positions_list):
    global initial_x_tor, initial_y_tor 
    global initial_x_leaves, initial_y_leaves
    global initial_x_spine, initial_y_spine
    global initial_x_exit, initial_y_exit
    global initial_x_server, initial_y_server, server_y
    
    if re.search("leaf",  name_n):
        initial_x_leaves += 150
        positions_list[name_n] = (initial_x_leaves,initial_y_leaves)
    elif re.search("spine",  name_n): 
        number = int(re.split(r'spine|\[|\]=.*', name_n)[1]) 
        
        if number > 2 and number % 2 == 1: 
            initial_x_spine +=  350
        else: 
            initial_x_spine += 150
          
        positions_list[name_n] = (initial_x_spine,initial_y_spine)
    elif re.search("tor", name_n) :
        initial_x_tor += 150
        positions_list[name_n] = (initial_x_tor,initial_y_tor)
    elif re.search("exit", name_n): 
        number = int(re.split(r'exit|\[|\]=.*', name_n)[1]) 
        if number > 2 and number % 2 == 1: 
            initial_x_exit +=  350
        else: 
            initial_x_exit += 150
        positions_list[name_n] = (initial_x_exit, initial_y_exit)
    elif re.search("server", name_n): 
        current_server_number = int(re.split(r"server|\[|\]", name_n)[1])
        server_y += 100
        positions_list[name_n] = (initial_x_server, server_y)    
        if (current_server_number % num_server_per_tor == 0) : 
            initial_x_server += 150
            server_y = initial_y_server
        

# returns two free ip addresses and their lan
def get_ip(): 
    global prefix
    global prefix1
    if prefix == 255 :
        prefix1 += 1
        prefix = 0
    ip1 = "10.0."+str(prefix1)+"."+str(prefix+1)+"/30"
    ip2 = "10.0."+str(prefix1)+"."+str(prefix+2)+"/30"
    lan = "10.0."+str(prefix1)+"."+str(prefix)+"/30"
    prefix += 4
    return ip1, ip2, lan



# returns the node (name) image for the graph
def get_image(name):
    if re.search("tor",  name):
        image = "file:///"+path+"/image/tor.png"
    elif re.search("spine", name): 
        image = "file:///"+path+"/image/spine.png"
    elif re.search("leaf", name):
        image = "file:///"+path+"/image/leaf.png"
    elif re.search("exit", name):
        image = "file:///"+path+"/image/exit.png"
    elif re.search("server", name): 
        image = "file:///"+path+"/image/server.png"
    return image


def skip_line(fp):
    line = fp.readline().strip()
    while re.search(r"tor[0-9]*\[2\]|server", line):
        #print("skip line: " + line)
        line = fp.readline().strip()
    #print(line)
    return line


current_server_net = 0
def get_servers_net(): 
    global current_server_net
    net = "200.0."+ str(current_server_net) +"."
    current_server_net += 1
    return net

def  add_server_lan_to_graph(server_index, tor_index, server_net, server_ip): 
    global clos_net, net, positions_list
    server_name = "server"+str(server_index)
    tor_name = "tor"+str(tor_index+1)
    transparent_node_name = "transparent"+str(server_index)
    server_net = server_net + "0/24"
    net[server_name] = ["0: "+ server_ip + " to " + tor_name + "<br>"]
    net[transparent_node_name] = [server_net]
    set_positions(server_name, positions_list)
    curr_posx,curr_posy = positions_list[server_name]
    image = get_image(server_name)
    if server_index % 3 == 1 : 
        clos_net.add_node(transparent_node_name,"",title="",shape="image",physics=False, x=curr_posx, y=curr_posy,image="transparent.png", hidden=True)
        clos_net.add_edge(transparent_node_name,tor_name, width=(0.1), title=server_net)
        clos_net.add_node(server_name,server_name,title=server_name+" neighbors:<br><br>",shape="image",physics=False, x=curr_posx - 100, y=curr_posy,image=image)
        clos_net.add_edge(transparent_node_name,server_name, width=(0.1), title=server_net)
    else : 
        clos_net.add_node(transparent_node_name,"",title="",shape="image",physics=False, x=curr_posx, y=curr_posy,image="transparent.png", hidden=True)
        clos_net.add_edge(transparent_node_name,"transparent"+str(server_index-1), width=(0.1), title=server_net)
        clos_net.add_node(server_name,server_name,title=server_name+" neighbors:<br><br>",shape="image",physics=False, x=curr_posx - 100, y=curr_posy,image=image)
        clos_net.add_edge(transparent_node_name,server_name, width=(0.1), title=server_net)



def server_ipconfig(): 
    current_server = 1
    for tor_index in range(num_tor): 
        server_net = get_servers_net()
        tor_ip = server_net +"1"
        open("tor"+str(tor_index+1)+".startup", "a").write("ifconfig eth2 "+ tor_ip +"/24 up\n")
        for server_index in range(num_server_per_tor): 
            server_ip = server_net + str(server_index+2)
            server_startup = open("server"+str(current_server)+".startup", "a")
            server_startup.write("ifconfig eth0 "+ server_ip +"/24 up\n")
            server_startup.write("route add default gw "+tor_ip+"\n")
            add_server_lan_to_graph(current_server, tor_index, server_net, server_ip)
            server_startup.close()
            current_server += 1




# reads the lab_unsort.conf file and writes all the .startup files
def ipconfig():
    print("Configuring the IPs and drawing the graph...")
    for item in files:
        if item.endswith(".startup"):
            os.remove( item )

    with open(filepath) as fp:  

        line1 = skip_line(fp)
        
        line2 = skip_line(fp)
        
        cnt = 2
        global positions_list
        while line1 and line2:

            n1 = re.split(r'\[|\]=', line1)
            name_n1 = n1[0]
            eth_n1 = n1[1]
            n2 = re.split(r'\[|\]=', line2)   
            name_n2 = n2[0]
            eth_n2 = n2[1]
           
            if(n1[2]==n2[2]):

               
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
                    set_positions(name_n1, positions_list)
                    curr_posx1,curr_posy1 = positions_list[name_n1]
                    image = get_image(name_n1)
                    clos_net.add_node(name_n1,name_n1,title=name_n1+" neighbors:<br><br>",shape="image", physics=False, x=curr_posx1, y=curr_posy1 ,image=image)                                                                                                                                                                                               

                if node2:
                    net[name_n2].append(eth_n2 + ": "+ ip2 + " to " + name_n1 + "<br>")
                    #node2["title"] += eth_n2 + ": "+ ip2 + " to " + name_n1 + "<br>"
                else: 
                    net[name_n2] = [eth_n2 + ": "+ ip2 + " to " + name_n1 + "<br>"]
                    set_positions(name_n2, positions_list)
                    curr_posx2,curr_posy2 = positions_list[name_n2]
                    image = get_image(name_n2)
                    clos_net.add_node(name_n2,name_n2,title=name_n2+" neighbors:<br><br>",shape="image",physics=False, x=curr_posx2, y=curr_posy2,image=image)
                
                clos_net.add_edge(name_n1,name_n2, width=(0.1), title=lan)
                
                #print("Line {}: {}".format(cnt, line1))
                line1 = skip_line(fp)
                cnt += 1
                #print("Line {}: {}".format(cnt, line2))
                line2 = skip_line(fp)
                cnt += 1
            else:
                print("lans don't match")
                
    server_ipconfig()

    for node in clos_net.nodes :
        net[node["id"]].sort()
        for item in net[node["id"]]: 
            node["title"] += item
        



        
    clos_net.show("clos.html")
    #webbrowser.open_new_tab("file:///"+path+"/clos.html")

