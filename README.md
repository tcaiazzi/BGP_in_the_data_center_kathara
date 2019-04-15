# Example of use of BGP in a data center using Katharà 
This is an example code for building a data center clos topology that use BGP for routing. 

## Pre-requisite

To run the example lab in this repository, you'll need katharà: 
 
https://github.com/KatharaFramework/Kathara

You need to build the docker image for katharà containers. Open the lab folder in a terminal and type: 

```
$ docker build -t kathara/frr .

```
You also need the pyvis lib for python3 to visualize the network topology. To download it open a terminal and type: 

```
$ python3 -m pip install pyvis

```

## Run the lab
To run the lab, go to the lab directory and type on terminal: 

```
$ python3 create_lab.py
$ lstart

```
The create_lab.py creates the configuration files for nodes and the network graph (clos.html).
You can open the clos.html file in a browser to check the network topology and the ip configuration.

To stop the lab, type on terminal: 

```
$ lclean

```

## Configure the lab
The number of spines, leaves and servers can be modified editing the build_net.py file: 

```
num_leafs = 4 #number of total leaves
num_server_pod = 2 #number of servers per pod (two leaves are considered a pod)
num_spine = 2 #number of spines

```
After, you'll need to run create_lab.py.

N.B. : we test only configuration with an even number of leaves and spines. 


## Examine the behaviour of BGP 
You can examine how BGP works in the lab. For example, if you run the lab with default configuration (2 spines, 4 leaves, 4 servers), open the spine1 terminal and type: 


```
root@spine1:/# telnet localhost bgpd 
root@spine1:/# frr 

Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.

Hello, this is FRRouting (version 7.0).
Copyright 1996-2005 Kunihiro Ishiguro, et al.


User Access Verification

Password: 

root@spine1:/# frr

frr> show ip bgp 
BGP table version is 32, local router ID is 10.0.255.1, vrf id 0
Default local pref 100, local AS 65499
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*  10.0.0.0/30      10.0.0.1                 0             0 65000 ?
*>                  0.0.0.0                  0         32768 ?
*  10.0.0.4/30      10.0.0.5                 0             0 65001 ?
*>                  0.0.0.0                  0         32768 ?
*  10.0.0.8/30      10.0.0.9                 0             0 65002 ?
*>                  0.0.0.0                  0         32768 ?
*  10.0.0.12/30     10.0.0.13                0             0 65003 ?
*>                  0.0.0.0                  0         32768 ?
*> 10.0.0.16/30     10.0.0.1                 0             0 65000 ?
*> 10.0.0.20/30     10.0.0.5                 0             0 65001 ?
*> 10.0.0.24/30     10.0.0.9                 0             0 65002 ?
*> 10.0.0.28/30     10.0.0.13                0             0 65003 ?
*= 10.0.0.32/30     10.0.0.5                 0             0 65001 ?
*>                  10.0.0.1                 0             0 65000 ?
*= 10.0.0.36/30     10.0.0.5                 0             0 65001 ?
*>                  10.0.0.1                 0             0 65000 ?
*> 10.0.0.40/30     10.0.0.9                 0             0 65002 ?
*=                  10.0.0.13                0             0 65003 ?
*> 10.0.0.44/30     10.0.0.9                 0             0 65002 ?
*=                  10.0.0.13                0             0 65003 ?
*  10.0.0.48/30     10.0.0.5                               0 65001 1 65000 ?
*>                  10.0.0.1                 0             0 65000 ?
*> 10.0.0.52/30     10.0.0.5                 0             0 65001 ?
*                   10.0.0.1                               0 65000 1 65001 ?
*  10.0.0.56/30     10.0.0.5                               0 65001 1 65000 ?
*>                  10.0.0.1                 0             0 65000 ?
*> 10.0.0.60/30     10.0.0.5                 0             0 65001 ?
*                   10.0.0.1                               0 65000 1 65001 ?
*> 10.0.0.64/30     10.0.0.9                 0             0 65002 ?
*                   10.0.0.13                              0 65003 3 65002 ?
*  10.0.0.68/30     10.0.0.9                               0 65002 3 65003 ?
*>                  10.0.0.13                0             0 65003 ?
*> 10.0.0.72/30     10.0.0.9                 0             0 65002 ?
*                   10.0.0.13                              0 65003 3 65002 ?
*  10.0.0.76/30     10.0.0.9                               0 65002 3 65003 ?
*>                  10.0.0.13                0             0 65003 ?
*> 10.0.0.80/30     0.0.0.0                  0         32768 ?
*> 10.0.0.84/30     0.0.0.0                  0         32768 ?

Displayed  22 routes and 38 total paths

```

You can notice that bgp multipath is working (the '=' means that the routes to the target have the same cost), so the control plane works correctly. 
If you want to check that also the data plane detects multipath routes, type on spine1 terminal (outside the bgp daemon): 

```
root@spine1:/# ip route show 10.0.0.40/30
10.0.0.40/30 proto bgp metric 20 
        nexthop via 10.0.0.9 dev eth4 weight 1 
        nexthop via 10.0.0.13 dev eth5 weight 1 
```

