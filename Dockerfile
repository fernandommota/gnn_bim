FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime
RUN apt-get update && \
      apt-get -y install sudo
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1010 ubuntu
RUN apt-get -y install curl
RUN apt-get -y install telnet
RUN apt-get -y install gcc
RUN apt-get -y install xutils-dev
RUN apt-get -y install libx11-6 
RUN apt-get -y install libxrender1
RUN apt-get -y install libxxf86vm-dev
RUN apt-get -y install libxfixes3
RUN apt-get -y install libxi-dev
RUN apt-get -y install libxkbcommon-x11-0
RUN apt-get -y install libsm6
RUN apt-get -y install libgl1-mesa-dev

USER ubuntu
WORKDIR /home/ubuntu

