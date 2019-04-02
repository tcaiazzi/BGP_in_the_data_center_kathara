import build_net
import ipconfig
import bgp_config

build_net.build_lab_conf()
ipconfig.ipconfig()
bgp_config.write_all_config()