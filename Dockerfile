FROM ubuntu:18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    apt-utils \
    apt-transport-https \ 
    iputils-ping \
    telnet \
    curl \
    gnupg \
    lsb-release \
    nano \
    net-tools \
    traceroute \
    paris-traceroute \
    dublin-traceroute \
    tcpdump \
    bind9 \
    apache2 \
    dnsutils \
    git \
    tar \
    wget \
    links \
    vim

RUN curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add -   
   
RUN echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) "frr-stable" | tee -a /etc/apt/sources.list.d/frr.list 

RUN apt-get update && apt-get install -y frr frr-pythontools

RUN sed -i -e 's/service/no service/' /etc/frr/vtysh.conf \
    && rm /etc/frr/frr.conf

RUN ln -s /etc/init.d/bind9 /etc/init.d/bind