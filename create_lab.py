import build_net
import ipconfig
import bgp_config

#this module creates the lab

build_net.build_lab_conf()
ipconfig.ipconfig()
bgp_config.write_all_config()