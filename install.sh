!/bin/bash
clear
echo "FabitManage Daemon v0.1-alpha Installer"
echo "==========================================="
echo "Press any key to start the installation, or press ^C to exit."
pause

clear
echo "Updating system and installing required packages..."
if [  -n "$(uname -a | grep Ubuntu)" ]; then
    apt-get -y update
    apt-get -y install git-core
else
    yum -y update
    yum -y install git
fi

clear
echo "Downloading components..."
git clone https://github.com/mariolatiffathy/fabitmanage-daemon.git fabitmanage-installer-tmp
mkdir -p /fabitmanage-daemon && cp ./fabitmanage-installer-tmp/daemon.py /fabitmanage-daemon
mkdir -p /fabitmanage-daemon/config && cp ./fabitmanage-installer-tmp/config/daemon.ini /fabitmanage-daemon/config

clear
echo "Removing temporary files..."
rm -rf ./fabitmanage-installer-tmp/