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
    apt-get -y install git-core quota cgroup-tools libcgroup-dev tmux python3.6
else
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm
    yum -y update
    yum -y install git tmux python36u python36u-libs python36u-devel python36u-pip libcgroup libcgroup-tools
fi

clear
echo "Downloading components..."
git clone https://github.com/mariolatiffathy/fabitmanage-daemon.git fabitmanage-installer-tmp
mkdir -p /fabitmanage-daemon && cp ./fabitmanage-installer-tmp/daemon.py /fabitmanage-daemon
mkdir -p /fabitmanage-daemon/config && cp ./fabitmanage-installer-tmp/config/daemon.ini /fabitmanage-daemon/config
mkdir -p /fabitmanage-daemon/data/images && cp ./fabitmanage-installer-tmp/data/images/Minecraft.fabitimage /fabitmanage-daemon/data/images

clear
echo "Installing fabitmanaged service..."
cp /usr/bin/python3.6 /usr/bin/fabitmanagedpy
cp /usr/bin/python3 /usr/bin/fabitmanagedpy
cp ./fabitmanage-installer-tmp/fabitmanaged.service /lib/systemd/system
systemctl daemon-reload

clear
echo "Installing required Python modules..."
fabitmanagedpy -m pip install -r ./fabitmanage-installer-tmp/requirements.txt

clear
echo "Removing temporary files..."
rm -rf ./fabitmanage-installer-tmp/