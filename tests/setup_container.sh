#!/bin/bash
lxc-create -n fabitmanage-container1 -t centos
lxc-stop -n fabitmanage-container1
lxc config set fabitmanage-container1 limits.cpu 2
lxc config set fabitmanage-container1 limits.memory 64MB
lxc-start -n fabitmanage-container1 -d
lxc-console -n fabitmanage-container1
