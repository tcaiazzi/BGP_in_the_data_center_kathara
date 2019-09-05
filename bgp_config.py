import os
import re
import shutil
import build_net
import glob

num_leaves = build_net.num_leaves
num_tor_pod=build_net.num_tor_per_pod
num_spine=build_net.num_spine
num_exit = build_net.num_exit

spine_asn = 65499 #starting asn number for spines (the first is 65500)
leaf_asn = 64999 #starting asn number for leaves (the first is 65000)
tor_asn = 0 #starting asn number for tors (the first is 1)

# variables used to assign router_id
spine_id=1
leaf_id=1
tor_id=1

# returns a free asn number for the node type of node (node_name)
def get_asn(node_name):
    global spine_asn
    global leaf_asn
    global tor_asn
  
    asn = None
    if re.search('spine', node_name):
        spine_asn += 1
        asn = spine_asn
    elif re.search('leaf|exit', node_name): 
        leaf_asn += 1
        asn = leaf_asn
    elif re.search('tor', node_name): 
        tor_asn += 1
        asn = tor_asn
    return asn

# creates all the directory needed in the lab by frr and bgp 
def create_dir():
    startup_files = glob.glob("*.startup")
 
    for item in startup_files:
        with open(item, "a") as startup:
            name = re.split(r'\.startup', item)[0]
            if not(item.startswith("server")):
                startup.write("/etc/init.d/frr start\n")
                startup.write("sysctl -w net.ipv4.fib_multipath_hash_policy=1\n")  #to enable ipv4 multipath 
                os.makedirs(name+"/etc/frr")
                with open(name+"/etc/frr/daemons", "w") as daemons:
                    daemons.write("zebra=yes\n")
                    daemons.write("bgpd=yes\n")
                with open(name+"/etc/frr/bgpd.conf", "w") as bgpd:
                    bgpd.write(
                        "hostname frr\n"
                        + "password frr\n"
                        + "enable password frr\n"
                    )
                    bgpd.write(
                        "\n\n"
                        + "ip prefix-list DC_LOCAL_SUBNET 5 permit 10.0.0.0/16 le 26\n"
                        + "ip prefix-list DC_LOCAL_SUBNET 10 permit 200.0.0.0/16 le 32\n"
                        + "route-map ACCEPT_DC_LOCAL permit 10\n"
                        + " match ip-address DC_LOCAL_SUBNET\n\n\n"
                    )
                    
                with open(name+"/etc/frr/zebra.conf", "w") as zebra:
                    zebra.write(
                        "hostname frr\n"
                        + "password frr\n"
                        + "enable password frr\n"
                    )          
            else:
                startup.write("/etc/init.d/apache2 start\n")
                os.makedirs(name+"/var/www/html")
                with open(name+"/var/www/html/index.html", "w") as index:
                    index.write("<html><body>This response comes from " + name + "</body></html>")

# writes the spine (spine_name) bgpd.conf file
def write_spine_bgpd(spine_name):
    global spine_id
    with open(spine_name+"/etc/frr/bgpd.conf", "a") as bgpd_conf:
   
        asn = get_asn(spine_name)
        bgpd_conf.write(
            "router bgp " + str(asn) + "\n"
            + " bgp router-id 10.0.255." + str(spine_id) +"\n"
            + " bgp bestpath as-path multipath-relax\n"
            + " bgp bestpath compare-routerid\n"    
            + " timers bgp 3 9\n" 
            + " neighbor fabric peer-group\n"
            + " neighbor fabric remote-as external\n"
            + " neighbor fabric advertisement-interval 0\n"
            + " neighbor fabric timers connect 5\n"
        )
        i = 2
        for i in range(2, num_leaves + 2 + num_exit):
            bgpd_conf.write(
              " neighbor eth" + str(i) + " interface peer-group fabric\n"
            )
        bgpd_conf.write(
            " address-family ipv4 unicast\n"
            + "  neighbor fabric activate\n"
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n" 
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )
        spine_id+=1

# writes the leaf (leaf_name) bgpd.conf file
def write_leaf_bgpd(leaf_name):
    global leaf_id
    with open(leaf_name+"/etc/frr/bgpd.conf", "a") as bgpd_conf:
        asn = get_asn(leaf_name)
        bgpd_conf.write(
            "router bgp " + str(asn) + "\n"
            + " timers bgp 3 9\n" 
            + " bgp router-id 10.0.254." + str(leaf_id) +"\n"
            + " bgp bestpath as-path multipath-relax\n"
            + " bgp bestpath compare-routerid\n"
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
        for i in range(num_spine+2, num_spine+2+num_tor_pod):
            bgpd_conf.write(
              " neighbor eth"+ str(i) + " interface peer-group TOR\n"
            )
        bgpd_conf.write(
            " address-family ipv4 unicast\n"
            + "  neighbor ISL activate\n"
            + "  neighbor TOR activate\n"
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n" 
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )
        leaf_id+=1


# writes the exit (exit_name) bgpd.conf file
def write_exit_bgpd(exit_name):
    global leaf_id
    with open(exit_name+"/etc/frr/bgpd.conf", "a") as bgpd_conf:
        asn = get_asn(exit_name)
        bgpd_conf.write(
            "router bgp " + str(asn) + "\n"
            + " timers bgp 3 9\n" 
            + " bgp router-id 10.0.254." + str(leaf_id) +"\n"
            + " bgp bestpath as-path multipath-relax\n"
            + " bgp bestpath compare-routerid\n"
            + " neighbor fabric peer-group\n"
            + " neighbor fabric remote-as external\n"
            + " neighbor fabric advertisement-interval 0\n"
            + " neighbor fabric timers connect 5\n"
        )
        i = 2
        for i in range(2, num_spine + 2):
            bgpd_conf.write(
              " neighbor eth"+ str(i) + " interface peer-group fabric\n"
            )
        bgpd_conf.write(
            " address-family ipv4 unicast\n"
            + "  neighbor fabric activate\n"
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n" 
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )
        leaf_id+=1

# writes the tor (tor_name) bgpd.conf file
def write_tor_bgpd(tor_name):
    global tor_id
    with open(tor_name+"/etc/frr/bgpd.conf", "a") as bgpd_conf:
        asn = get_asn(tor_name)
        bgpd_conf.write(
            "router bgp " + str(asn) + "\n"
            + " bgp router-id " + str(tor_id)+"."+str(tor_id)+"."+str(tor_id)+"."+str(tor_id) +"\n"
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
            + "  redistribute connected route-map ACCEPT_DC_LOCAL\n" 
            + "  maximum-paths 64\n"
            + " exit-address-family\n"
        )
        tor_id+=1

# writes all the bgpd.conf files
def write_all_config(): 
    print("Creating BGP configurations...")
    create_dir()
    for i in range(1, num_spine+1):
        write_spine_bgpd("spine"+str(i))

    for i in range(1, num_leaves+1): 
        write_leaf_bgpd("leaf"+str(i))

    for i in range(1, num_exit+1): 
        write_exit_bgpd("exit"+str(i))

    number_of_tor = num_tor_pod * int((num_leaves/2))
    for i in range(1, number_of_tor+1):     
        write_tor_bgpd("tor"+str(i))