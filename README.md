# Example of use of BGP in a data center using Katharà 
This is an example code for building a data center clos topology that use BGP for routing. 

## Pre-requisite

To run the example lab in this repository, you'll need katharà: 
 
https://github.com/KatharaFramework/Kathara

You need to build the docker image for katharà containers. Open the lab folder in a terminal and type: 

```
$ docker build -t kathara/frr .

```

## Run the lab
To run the lab, type on terminal: 

```
$ python3 create_lab.py
$ lstart

```

To stop the lab, type on terminal: 

```
$ lclean

```

## Configure the lab
The number of spines, leaves and servers can be modified editing the buil_net.py file: 

```
num_leafs = 4 #number of total leaves
num_server_pod = 2 #number of servers per pod (two leaves are considered a pod)
num_spine = 2 #number of spines

```
After, you'll need to run create_lab.py.

N.B. : we test only configuration with an even number of leaves and spines. 
