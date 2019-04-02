import os , sys
import string
num_leaves = 4
num_server_pod = 2
num_spine = 2
# 0 and 1 for connection 
start_port = 2
current_id = "@"
number = 0

def get_lan():
    global number
    global current_id
    asci_int = ord(current_id[0]) 
    if(chr(asci_int)=='Z'):
        number = number + 1
        asci_int = ord('A')
    else:
        asci_int += 1
    current_id = chr(asci_int)
    return chr(asci_int)+str(number)
   
def write_leaf_spine(lab,lab_unsort,port_for_spine,port_for_leaf,current_id,spine_number,leaf_number):

    current_id = get_lan()
    lab.write("leaf0"+str(leaf_number)+"["+str(port_for_spine)+"]=\""+current_id+"\"\n")
    lab.write("spine0"+str(spine_number)+"["+str(port_for_leaf)+"]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(leaf_number)+"["+str(port_for_spine)+"]=\""+current_id+"\"\n")
    lab_unsort.write("spine0"+str(spine_number)+"["+str(port_for_leaf)+"]=\""+current_id+"\"\n")

def connect_leaves(lab,lab_unsort,leaf_number,current_id):
    current_id = get_lan()
    lab.write("leaf0"+str(leaf_number)+"[0]=\""+current_id+"\"\n")
    lab.write("leaf0"+str(leaf_number+1)+"[0]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(leaf_number)+"[0]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(leaf_number+1)+"[0]=\""+current_id+"\"\n")

    current_id = get_lan()
    lab.write("leaf0"+str(leaf_number)+"[1]=\""+current_id+"\"\n")
    lab.write("leaf0"+str(leaf_number+1)+"[1]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(leaf_number)+"[1]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(leaf_number+1)+"[1]=\""+current_id+"\"\n")

def connect_server_to_leaf(lab,lab_unsort,server_number,num_pods,current_id,port_for_server):
    current_id = get_lan()
    lab.write("server0"+str(server_number)+"[0]=\""+current_id+"\"\n")
    lab.write("server0"+str(server_number)+"[image]=frr\n")
    lab.write("leaf0"+str(num_pods)+"["+str(port_for_server)+"]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(num_pods)+"["+str(port_for_server)+"]=\""+current_id+"\"\n")
    lab_unsort.write("server0"+str(server_number)+"[0]=\""+current_id+"\"\n")

    current_id = get_lan()
    lab.write("server0"+str(server_number)+"[1]=\""+current_id+"\"\n")
    lab.write("leaf0"+str(num_pods+1)+"["+str(port_for_server)+"]=\""+current_id+"\"\n")
    lab_unsort.write("server0"+str(server_number)+"[1]=\""+current_id+"\"\n")
    lab_unsort.write("leaf0"+str(num_pods+1)+"["+str(port_for_server)+"]=\""+current_id+"\"\n")

def connect_spine_to_spine(lab,lab_unsort,spine_number,current_id):
    current_id = get_lan()
    lab.write("spine0"+str(spine_number)+"[0]=\""+current_id+"\"\n")
    lab.write("spine0"+str(spine_number+1)+"[0]=\""+current_id+"\"\n")
    lab_unsort.write("spine0"+str(spine_number)+"[0]=\""+current_id+"\"\n")
    lab_unsort.write("spine0"+str(spine_number+1)+"[0]=\""+current_id+"\"\n")
      
    current_id = get_lan()
    lab.write("spine0"+str(spine_number)+"[1]=\""+current_id+"\"\n")
    lab.write("spine0"+str(spine_number+1)+"[1]=\""+current_id+"\"\n")
    lab_unsort.write("spine0"+str(spine_number)+"[1]=\""+current_id+"\"\n")
    lab_unsort.write("spine0"+str(spine_number+1)+"[1]=\""+current_id+"\"\n")
       
def build_lab_conf( ):
    global current_id
    lab  = open("lab.conf","w",)
    lab_unsort = open("lab_unsort.conf","w",)
    num_leaf = 0 
    if( num_spine%2 == 0 ):
        port_for_leaf = 2
    else: 
        port_for_leaf = 0

    port_for_spine = 2
    num_pods = 0
    
    for i in range(num_spine):
        lab.write("spine0"+str(i+1)+"[image]=frr \n")
        for j in range(num_leaves): 
            write_leaf_spine(lab,
                             lab_unsort,
                             port_for_spine,
                             port_for_leaf,
                             current_id,i+1,j+1)

            if( i==0 ):
                lab.write("leaf0"+str(j+1)+"[image]=frr\n")
            port_for_leaf += 1
        port_for_leaf = 2 
        port_for_spine +=1

    num_pair_to_connect = num_leaves/2
    start_id = 0
    for i in range (int(num_pair_to_connect)):
        connect_leaves(lab,
                      lab_unsort,
                      start_id+1,
                      current_id)
        start_id+=2

    num_build_server = 0
    for j in range(int(num_leaves/2)):
        port_for_server = port_for_spine
        for k in range(num_server_pod):
            connect_server_to_leaf(lab,
                                   lab_unsort,
                                   num_build_server+1,
                                   num_pods+1,
                                   current_id,
                                   port_for_server)
           
            port_for_server += 1
            num_build_server += 1
        num_pods+=2
    
    num_spine_to_connect = 0
    for i in range(int(num_spine/2)):
        connect_spine_to_spine(lab,
                               lab_unsort,
                               num_spine_to_connect+1,
                               current_id)
        num_spine_to_connect += 2

    data=open("lab.conf").readlines()
    data.sort()
    lab  = open("lab.conf","w",)
    for i in range(len(data)):
        lab.write(data[i])

