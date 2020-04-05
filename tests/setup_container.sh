#!/bin/bash
lxc-create -n fabitmanage-container1 -t centos
lxc-stop -n fabitmanage-container1
echo 'lxc.cgroup.cpu.shares = 2' >> /var/lib/lxc/fabitmanage-container1/config
echo 'lxc.cgroup.memory.limit_in_bytes = 64M' >> /var/lib/lxc/fabitmanage-container1/config
lxc-start -n fabitmanage-container1 -d
lxc-console -n fabitmanage-container1
