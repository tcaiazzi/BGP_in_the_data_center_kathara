import os
import re
import shutil
import build_net

num_leaves = build_net.num_leaves
num_server_pod=build_net.num_server_pod
num_spine=build_net.num_spine


spine_asn = 65499 #starting asn number for spines (the first is 65500)
leaf_asn = 64999 #starting asn number for leaves (the first is 65000)
server_asn = 0 #starting asn number for servers (the first is 1)

# variables used to assign router_id
spine_id=1
leaf_id=1
server_id=1

# returns a free asn number for the node type of node (node_name)
def get_asn(node_name):
    global spine_asn
    global leaf_asn
    global server_asn
    print(node_name)
    asn = None
    if re.search('spine', node_name):
        spine_asn += 1
        asn = spine_asn
    elif re.search('leaf', node_name): 
        leaf_asn += 1
        asn = leaf_asn
    elif re.search('server', node_name): 
        server_asn += 1
        asn = server_asn
    return asn

# creates all the directory needed in the lab by frr and bgp 
def create_dir():
    files = os.listdir('.')
    for item in files:
        if item.endswith(".startup"):
            name = re.split('\.startup', item)[0]
            if os.path.exists(name): 
                shutil.rmtree(name)
        
    for item in files:
        if item.endswith(".startup"):
            startup = open(item, "a")
            startup.write("/etc/init.d/frr start\n")
            startup.write("sysctl -w net.ipv4.fib_multipath_hash_policy=1")  #to enable ipv4 multipath 
            name = re.split('\.startup', item)[0]
            print(name)
            os.mkdir(name)
            os.mkdir(name+"/etc")
            os.mkdir(name+"/etc/frr")
            daemons = open(name+"/etc/frr/daemons", "w")
            daemons.write("zebra=yes\n")
            daemons.write("bgpd=yes\n")
            bgpd = open(name+"/etc/frr/bgpd.conf", "w")
            bgpd.write(
                  "hostname frr\n"
                + "password frr\n"
                + "enable password frr\n"
            )

# writes the spine (spine_name) bgpd.conf file
def write_spine_bgpd(spine_name):
    global spine_id
    bgpd_conf=open(spine_name+"/etc/frr/bgpd.conf", "a")
    print(spine_name)
    asn = get_asn(spine_name)
    bgpd_conf.write(
        "router bgp " + str(asn) + "\n"
        + " bgp router-id 10.0.255." + str(spine_id) +"\n"
        + " timers bgp 3 9\n" 
        + " neighbor ISL peer-group\n"
        + " neighbor ISL remote-as external\n"
        + " neighbor ISL advertisement-interval 0\n"
        + " neighbor ISL timers connect 5\n"
    )
    i = 2
    for i in range(2, num_leaves + 2):
        bgpd_conf.write(
          " neighbor eth"+ str(i) + " interface peer-group ISL\n"  
        )
    bgpd_conf.write(
        " bgp bestpath as-path multipath-relax\n"
        + " address-family ipv4 unicast\n"
        + "  neighbor ISL activate\n"
        + "  redistribute connected\n" 
        + "  maximum-paths 64\n"
        + " exit-address-family\n"
    )
    spine_id+=1

# writes the leaf (leaf_name) bgpd.conf file
def write_leaf_bgpd(leaf_name):
    global leaf_id
    bgpd_conf=open(leaf_name+"/etc/frr/bgpd.conf", "a")
    asn = get_asn(leaf_name)
    bgpd_conf.write(
        "router bgp " + str(asn) + "\n"
        + " timers bgp 3 9\n" 
        + " bgp router-id 10.0.254." + str(leaf_id) +"\n"
        + " neighbor ISL peer-group\n"
        + " neighbor ISL remote-as external\n"
        + " neighbor ISL advertisement-interval 0\n"
        + " neighbor ISL timers connect 5\n"
    )
    i = 2
    for i in range(2, num_spine + 2):
        bgpd_conf.write(
          " neighbor eth"+ str(i) + " interface peer-group ISL\n"  
        )
    bgpd_conf.write(
        " neighbor TOR peer-group\n"
        + " neighbor TOR remote-as external\n"
        + " neighbor TOR advertisement-interval 0\n"
        + " neighbor TOR timers connect 5\n"
    )
    i = num_spine
    for i in range(num_spine+2, num_spine+2+num_server_pod):
        bgpd_conf.write(
          " neighbor eth"+ str(i) + " interface peer-group TOR\n"  
        )
    bgpd_conf.write(
        " bgp bestpath as-path multipath-relax\n"
        + " address-family ipv4 unicast\n"
        + "  neighbor ISL activate\n"
        + "  neighbor TOR activate\n"
        + "  redistribute connected\n" 
        + "  maximum-paths 64\n"
        + " exit-address-family\n"
    )
    leaf_id+=1

# writes the server (server_name) bgpd.conf file
def write_server_bgpd(server_name):
    global server_id
    bgpd_conf=open(server_name+"/etc/frr/bgpd.conf", "a")
    asn = get_asn(server_name)
    bgpd_conf.write(
        "router bgp " + str(asn) + "\n"
        + " bgp router-id " + str(server_id)+"."+str(server_id)+"."+str(server_id)+"."+str(server_id) +"\n"
        + "timers bgp 3 9\n" )
    bgpd_conf.write(
        " neighbor TOR peer-group\n"
        + " neighbor TOR remote-as external\n"
        + " neighbor TOR advertisement-interval 0\n"
        + " neighbor TOR timers connect 5\n"
    )
    i = 0
    for i in range(0,2):
        bgpd_conf.write(
          " neighbor eth"+ str(i) + " interface peer-group TOR\n"  
        )
    bgpd_conf.write(
        " bgp bestpath as-path multipath-relax\n"
        + "  address-family ipv4 unicast\n"
        + "  neighbor TOR activate\n" 
        + "  maximum-paths 64\n"
        + " exit-address-family\n"
    )
    server_id+=1

# writes all the bgpd.conf files
def write_all_config(): 
    create_dir()
    for i in range(1, num_spine+1):
        write_spine_bgpd("spine"+str(i))

    for i in range(1, num_leaves+1): 
        write_leaf_bgpd("leaf"+str(i))

    number_of_server = num_server_pod * int((num_leaves/2))
    for i in range(1, number_of_server+1):     
        write_server_bgpd("server"+str(i))