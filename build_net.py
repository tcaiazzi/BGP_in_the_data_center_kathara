import os , sys
import string


num_leaves = 4  #number of leaves 
num_tor_per_pod = 2 #number of tor per pod (a pod is made by two leaves)
num_spine = 2 #number of spine
num_exit = 2  #number of exit nodes
num_server_per_tor = 3 #number of servers for each ToR

num_server = int(num_server_per_tor * (num_leaves/2))
num_tor = int(num_tor_per_pod * (num_leaves/2))
# 0 and 1 for connection 
start_port = 2
current_id1 = "A"
current_id2 = "A"
current_id3 = "A"
current_id4 = "@"

#This module is used to build the lab.conf file

def get_lan():
    global current_id1, current_id2, current_id3, current_id4
    asci_int1 = ord(current_id1[0])
    asci_int2 = ord(current_id2[0])
    asci_int3 = ord(current_id3[0])
    asci_int4 = ord(current_id4[0])

    if(asci_int4 >= ord('Z')):
        asci_int3 += 1
        asci_int4 = ord('A')
    else:
        asci_int4 += 1

    if(asci_int3 >= ord('Z')):
        asci_int2 += 1
        asci_int3 = ord('A')

    if(asci_int2 >= ord('Z')):
        asci_int1 += 1
        asci_int2 = ord('A')

    current_id1 = chr(asci_int1)
    current_id2 = chr(asci_int2)
    current_id3 = chr(asci_int3)
    current_id4 = chr(asci_int4)

    return current_id1 + current_id2 + current_id3 + current_id4

# attaches in lab.conf a leaf to a spine
def connect_leaf_to_spine(lab,port_for_spine,port_for_leaf,spine_number,leaf_number):
    current_id = get_lan()
    lab.write("leaf"+str(leaf_number)+"["+str(port_for_spine)+"]=\""+current_id+"\"\n")
    lab.write("spine"+str(spine_number)+"["+str(port_for_leaf)+"]=\""+current_id+"\"\n")

# attaches two leaves (leaf_number and leaf_number+1)
def connect_leaves(lab,leaf_number):
    current_id = get_lan()
    lab.write("leaf"+str(leaf_number)+"[0]=\""+current_id+"\"\n")
    lab.write("leaf"+str(leaf_number+1)+"[0]=\""+current_id+"\"\n")

    current_id = get_lan()
    lab.write("leaf"+str(leaf_number)+"[1]=\""+current_id+"\"\n")
    lab.write("leaf"+str(leaf_number+1)+"[1]=\""+current_id+"\"\n")

# connects a tor (tor_number) to a pair of leaves (leaf_number and leaf_number+1) on leaf_interface
def connect_tor_to_leaf(lab,tor_number,leaf_number,leaf_interface):
    current_id = get_lan()
    lab.write("tor"+str(tor_number)+"[0]=\""+current_id+"\"\n")
    lab.write("tor"+str(tor_number)+"[image]=frr\n")
    lab.write("leaf"+str(leaf_number)+"["+str(leaf_interface)+"]=\""+current_id+"\"\n")
    
    current_id = get_lan()
    lab.write("tor"+str(tor_number)+"[1]=\""+current_id+"\"\n")
    lab.write("leaf"+str(leaf_number+1)+"["+str(leaf_interface)+"]=\""+current_id+"\"\n")

# connects two spine each other (spine_number and spine_number + 1)
def connect_spine_to_spine(lab,spine_number):
    current_id = get_lan()
    lab.write("spine"+str(spine_number)+"[0]=\""+current_id+"\"\n")
    lab.write("spine"+str(spine_number+1)+"[0]=\""+current_id+"\"\n")
      
    current_id = get_lan()
    lab.write("spine"+str(spine_number)+"[1]=\""+current_id+"\"\n")
    lab.write("spine"+str(spine_number+1)+"[1]=\""+current_id+"\"\n")
    
def connect_exit_to_spine(lab, exit_number, spine_number, exit_interface_spine, spine_interface_exit): 
    current_id = get_lan()
    lab.write("spine"+str(spine_number)+"["+str(spine_interface_exit)+"]=\""+current_id+"\"\n")
    lab.write("exit"+str(exit_number)+"["+str(exit_interface_spine)+"]=\""+current_id+"\"\n")
    
def connect_exit_to_exit(lab, exit1, exit2): 
    current_id = get_lan()
    lab.write("exit"+str(exit1)+"[0]=\""+current_id+"\"\n")
    lab.write("exit"+str(exit2)+"[0]=\""+current_id+"\"\n")
      
    current_id = get_lan()
    lab.write("exit"+str(exit1)+"[1]=\""+current_id+"\"\n")
    lab.write("exit"+str(exit2)+"[1]=\""+current_id+"\"\n")

def connect_server_to_tor(lab, server_number, server_lan): 
    lab.write("server"+str(server_number)+"[0]=\""+server_lan+"\"\n")
    

def create_tor_interface_to_servers(lab, tor_number, tor_interface_to_servers, server_lan): 
    lab.write("tor"+str(tor_number)+"["+str(tor_interface_to_servers)+"]=\""+server_lan+"\"\n")

 # writes the lab.conf file    
def build_lab_conf( ):
    print("Building the lab configuration ...")
    global current_id
    lab  = open("lab.conf","w")
    
    if( num_spine%2 == 0 ):
        port_for_leaf = 2
    else: 
        port_for_leaf = 0

    port_for_spine = 2
    num_pods = 0
    exit_interface_spine = 2
    spine_interface_exit = num_leaves + 2
    
    for i in range(num_spine):
        lab.write("spine"+str(i+1)+"[image]=frr \n")
        for j in range(num_leaves): 
            connect_leaf_to_spine(lab, port_for_spine, port_for_leaf, i+1,j+1)

            if( i==0 ):
                lab.write("leaf"+str(j+1)+"[image]=frr\n")
            port_for_leaf += 1
        
        port_for_leaf = 2 
        port_for_spine +=1
        
        spine_interface_exit = num_leaves + 2 if num_spine > 1 else num_leaves

        for exit_index in range(num_exit):
            #print("connect exit"+str(exit_index+1) + " to spine"+str(i+1))
            connect_exit_to_spine(lab, exit_index+1, i+1, exit_interface_spine, spine_interface_exit )
            if( i == 0): 
                lab.write("exit"+str(exit_index+1)+"[image]=frr\n")
            spine_interface_exit += 1
        exit_interface_spine += 1
        


    num_pair_to_connect = num_leaves/2
    start_id = 0
    for i in range (int(num_pair_to_connect)):
        connect_leaves(lab, start_id+1)
        start_id+=2

    num_build_tor = 0
    for j in range(int(num_leaves/2)):
        port_for_tor = port_for_spine
        for k in range(num_tor_per_pod):
            connect_tor_to_leaf(lab, num_build_tor+1, num_pods+1, port_for_tor)
           
            port_for_tor += 1
            num_build_tor += 1
        num_pods+=2

    
    server_index = 1
    
    for tor_index in range(int(num_tor_per_pod*(num_leaves/2))):
        #print(tor_index)
        tor_interface_to_servers = 2
        server_lan = get_lan()
        create_tor_interface_to_servers(lab, tor_index+1, tor_interface_to_servers,  server_lan)
        for server in range(num_server_per_tor):            
            connect_server_to_tor(lab, server_index, server_lan)
            server_index += 1
    
    num_spine_to_connect = 0
    for i in range(int(num_spine/2)):
        connect_spine_to_spine(lab, num_spine_to_connect+1)
        num_spine_to_connect += 2
    
    exit_index = 1
    for i in range(int(num_exit/2)): 
        connect_exit_to_exit(lab, exit_index, exit_index+1)
        exit_index += 2
        
    lab.close()