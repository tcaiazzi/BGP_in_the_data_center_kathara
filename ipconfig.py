import re 
import os
import build_net
import ipaddress

filepath = 'lab.conf'  
path = os.path.dirname(os.path.realpath(__file__))

base_ip = u"10.0.0.0"

num_server_per_tor =  build_net.num_server_per_tor
num_tor = build_net.num_tor


# returns two free ip addresses and their lan
def get_ip():
    global base_ip

    ip1 = ipaddress.ip_address(base_ip) + 1
    ip2 = ipaddress.ip_address(base_ip) + 2
    lan = ipaddress.ip_address(base_ip)

    base_ip = ipaddress.ip_address(base_ip) + 4

    return str(ip1) + "/30", str(ip2) + "/30", str(lan) + "/30"


current_server_net = u"200.0.0.0"
def get_servers_net(): 
    global current_server_net
    net = ipaddress.ip_address(current_server_net)
    current_server_net = ipaddress.ip_address(current_server_net) + 256
    return net

def server_ipconfig(): 
    current_server = 1
    for tor_index in range(num_tor): 
        server_net = get_servers_net()
        tor_ip = server_net + 1

        with open("tor"+str(tor_index+1)+".startup", "a") as tor_startup:
            tor_startup.write("ifconfig eth2 "+ str(tor_ip) +"/24 up\n")

        for server_index in range(num_server_per_tor): 
            server_ip = server_net + server_index + 2
            with open("server"+str(current_server)+".startup", "a") as server_startup:
                server_startup.write("ifconfig eth0 "+ str(server_ip) +"/24 up\n")
                server_startup.write("route add default gw "+ str(tor_ip) +"\n")
            current_server += 1

def skip_line(fp):
    line = fp.readline().strip()

    while re.search(r"tor[0-9]*\[2\]|server|image", line):
        line = fp.readline().strip()

    return re.split(r'\[|\]=', line)

# reads the lab_unsort.conf file and writes all the .startup files
def ipconfig():
    print("Configuring the IPs...")

    with open(filepath) as fp:  

        line1 = skip_line(fp)    
        line2 = skip_line(fp)
        
        while line1!=[''] and line2!=['']:

            device_name1, eth_num1, lan_name1 = line1
            device_name2, eth_num2, lan_name2 = line2
           
            if(lan_name1==lan_name2):

                ip1, ip2, lan = get_ip()
                with open(device_name1+".startup", "a") as file1:
                    file1.write("ifconfig eth"+str(int(eth_num1))+" "+ ip1 +" up\n" )
                
                with open(device_name2+".startup", "a") as file2:
                    file2.write("ifconfig eth"+str(int(eth_num2))+" "+ ip2 +" up\n" )

                line1 = skip_line(fp)    
                line2 = skip_line(fp)
            else:
                raise Exception("Lans don't match " + lan_name1 + " " + lan_name2)

    server_ipconfig()