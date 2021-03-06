# BGP in a data center using Katharà 
This is an example code for building a data center 3-tier clos topology with single-attached servers, that use BGP for routing.

All the nodes in the network use the default FRRouting ip protocol suite: 
https://frrouting.org/

## Pre-requisite

To run the example lab in this repository, you'll need katharà: 
 
https://github.com/KatharaFramework/Kathara

N.B. : Keep update your katharà version! See: 

https://github.com/KatharaFramework/Kathara/wiki/Update


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
The number of spines, leaves, ToRs and servers can be modified editing the build_net.py file: 

```
num_leaves = 4  #number of leaves 
num_tor_per_pod = 2 #number of tor per pod (a pod is made by two leaves)
num_spine = 2 #number of spine
num_exit = 2  #number of exit nodes
num_server_per_tor = 3 #number of servers for each ToR

```
After, you'll need to run create_lab.py.

N.B. : we test only configuration with an even number of leaves and spines. 


## Examine the behaviour of BGP 
You can examine how BGP works in the lab. For example, if you run the lab with default configuration (2 spines, 4 leaves, 4 ToRs, 12 servers), open the spine1 terminal and type: 


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
BGP table version is 38, local router ID is 10.0.255.1, vrf id 0
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
*  10.0.0.16/30     10.0.0.18                0             0 65004 ?
*>                  0.0.0.0                  0         32768 ?
*  10.0.0.20/30     10.0.0.22                0             0 65005 ?
*>                  0.0.0.0                  0         32768 ?
*> 10.0.0.24/30     10.0.0.1                 0             0 65000 ?
*> 10.0.0.28/30     10.0.0.5                 0             0 65001 ?
*> 10.0.0.32/30     10.0.0.9                 0             0 65002 ?
*> 10.0.0.36/30     10.0.0.13                0             0 65003 ?
*> 10.0.0.40/30     10.0.0.18                0             0 65004 ?
*> 10.0.0.44/30     10.0.0.22                0             0 65005 ?
*= 10.0.0.48/30     10.0.0.5                 0             0 65001 ?
*>                  10.0.0.1                 0             0 65000 ?
*= 10.0.0.52/30     10.0.0.5                 0             0 65001 ?
*>                  10.0.0.1                 0             0 65000 ?
*> 10.0.0.56/30     10.0.0.9                 0             0 65002 ?
*=                  10.0.0.13                0             0 65003 ?
*> 10.0.0.60/30     10.0.0.9                 0             0 65002 ?
*=                  10.0.0.13                0             0 65003 ?
*  10.0.0.64/30     10.0.0.5                               0 65001 1 ?
*>                  10.0.0.1                 0             0 65000 ?
*  10.0.0.68/30     10.0.0.1                               0 65000 1 ?
*>                  10.0.0.5                 0             0 65001 ?
*  10.0.0.72/30     10.0.0.5                               0 65001 2 ?
*>                  10.0.0.1                 0             0 65000 ?
*  10.0.0.76/30     10.0.0.1                               0 65000 2 ?
*>                  10.0.0.5                 0             0 65001 ?
*  10.0.0.80/30     10.0.0.13                              0 65003 3 ?
*>                  10.0.0.9                 0             0 65002 ?
*  10.0.0.84/30     10.0.0.9                               0 65002 3 ?
*>                  10.0.0.13                0             0 65003 ?
*  10.0.0.88/30     10.0.0.13                              0 65003 4 ?
*>                  10.0.0.9                 0             0 65002 ?
*  10.0.0.92/30     10.0.0.9                               0 65002 4 ?
*>                  10.0.0.13                0             0 65003 ?
*> 10.0.0.96/30     0.0.0.0                  0         32768 ?
*> 10.0.0.100/30    0.0.0.0                  0         32768 ?
*= 10.0.0.104/30    10.0.0.22                0             0 65005 ?
*>                  10.0.0.18                0             0 65004 ?
*= 10.0.0.108/30    10.0.0.22                0             0 65005 ?
*>                  10.0.0.18                0             0 65004 ?
*= 200.0.0.0/24     10.0.0.5                               0 65001 1 ?
*>                  10.0.0.1                               0 65000 1 ?
*= 200.0.1.0/24     10.0.0.5                               0 65001 2 ?
*>                  10.0.0.1                               0 65000 2 ?
*> 200.0.2.0/24     10.0.0.9                               0 65002 3 ?
*=                  10.0.0.13                              0 65003 3 ?
*> 200.0.3.0/24     10.0.0.9                               0 65002 4 ?
*=                  10.0.0.13                              0 65003 4 ?

Displayed  32 routes and 56 total paths


```

You can notice that bgp multipath is working (the '=' means that the routes to the target have the same cost), so the control plane works correctly. 
If you want to check that also the data plane detects multipath routes, type on spine1 terminal (outside the bgp daemon): 

```
root@spine1:/# ip route show 200.0.0.1/24
200.0.0.0/24 proto bgp metric 20 
        nexthop via 10.0.0.1 dev eth2 weight 1 
        nexthop via 10.0.0.5 dev eth3 weight 1 
```

## Verify High Availability

Using a routing protocol such as BGP or OSPF means that as long as one spine is still running, the network will automatically learn a new route and keep the fabric connected. This means that you can do rolling upgrades one spine at a time without incurring any downtime.

Open server1 terminal, and use traceroute to verify the path to server10 (200.0.3.2 if you use the default configuration) :

```

root@server1:/# traceroute 200.0.3.2
traceroute to 200.0.3.2 (200.0.3.2), 30 hops max, 60 byte packets
 1  200.0.0.1 (200.0.0.1)  0.094 ms  0.026 ms  0.019 ms
 2  10.0.0.65 (10.0.0.65)  0.056 ms 10.0.0.70 (10.0.0.70)  0.045 ms 10.0.0.65 (10.0.0.65)  0.027 ms
 3  10.0.0.2 (10.0.0.2)  0.052 ms 10.0.0.30 (10.0.0.30)  0.104 ms 10.0.0.2 (10.0.0.2)  0.088 ms
 4  10.0.0.37 (10.0.0.37)  0.060 ms 10.0.0.9 (10.0.0.9)  0.046 ms 10.0.0.37 (10.0.0.37)  0.043 ms
 5  10.0.0.90 (10.0.0.90)  0.078 ms  0.052 ms  0.049 ms
 6  200.0.3.2 (200.0.3.2)  0.137 ms  0.212 ms  0.112 ms

```

Try to ping from server1 to server10. While the ping is running, open leaf1 terminal and shutdown its eth4 (the one connected to tor1, the ToR of server1):

```
root@leaf1:/# ifconfig eth4 down

```

you can notice that the ping stops for a while, and then restarts! 