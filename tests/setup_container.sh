#!/bin/bash
useradd -m -d /home/fabitmanage/daemon-data/container1 -p $(openssl passwd -1 FabitContainerPasswd) fabitmanage-container1
