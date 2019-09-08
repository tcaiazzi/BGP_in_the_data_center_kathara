import build_net
import ipconfig
import bgp_config
import os
import shutil

#this module creates the lab

lab_path = "lab/"
if(os.path.isdir(lab_path)):
    shutil.rmtree(lab_path)

os.mkdir(lab_path)
os.chdir(lab_path)

build_net.build_lab_conf()
ipconfig.ipconfig()
bgp_config.write_all_config()