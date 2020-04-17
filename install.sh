!/bin/bash
clear
echo "Krabssy Daemon v0.1-alpha Installer"
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
git clone https://github.com/mariolatiffathy/krabssy-daemon.git krabssy-installer-tmp
mkdir -p /krabssy-daemon && cp ./krabssy-installer-tmp/daemon.py /krabssy-daemon
mkdir -p /krabssy-daemon/config && cp ./krabssy-installer-tmp/config/daemon.ini /krabssy-daemon/config
mkdir -p /krabssy-daemon/data/images && cp ./krabssy-installer-tmp/data/images/Minecraft.krabssyimage /krabssy-daemon/data/images

clear
echo "Installing krabssyd service..."
cp /usr/bin/python3.6 /usr/bin/krabssydpy
cp /usr/bin/python3 /usr/bin/krabssydpy
cp ./krabssy-installer-tmp/krabssyd.service /lib/systemd/system
systemctl daemon-reload

clear
echo "Installing required Python modules..."
krabssydpy -m pip install -r ./krabssy-installer-tmp/requirements.txt

clear
echo "Removing temporary files..."
rm -rf ./krabssy-installer-tmp/