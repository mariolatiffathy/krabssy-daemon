!/bin/bash
clear
echo "Krabssy Daemon v0.1-alpha Installer"
echo "==========================================="
echo "Press any key to start the installation, or press ^C to exit."
pause

clear
echo "Updating system and installing required packages..."
if [  -n "$(uname -a | grep Ubuntu)" ]; then
    add-apt-repository ppa:deadsnakes/ppa
    apt-get -y update
    for i in git-core quota cgroup-tools libcgroup-dev tmux python3.6 curl python-dev python3-dev python3.6-dev; do 
        apt-get -y install $i 
    done
else
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm
    yum -y update
    for i in git tmux python36u python36u-libs python36u-devel python36u-pip libcgroup libcgroup-tools curl python-devel python3-devel python3.6-devel python36-devel python36u-devel; do 
        yum -y install $i 
    done
fi

clear
echo "Downloading components..."
git clone https://github.com/mariolatiffathy/krabssy-daemon.git krabssy-installer-tmp
mkdir -p /krabssy-daemon && cp ./krabssy-installer-tmp/daemon.py /krabssy-daemon
mkdir -p /krabssy-daemon/config && cp ./krabssy-installer-tmp/config/daemon.ini /krabssy-daemon/config
mkdir -p /krabssy-daemon/data/images && cp ./krabssy-installer-tmp/data/images/Minecraft.krabssyimage /krabssy-daemon/data/images

clear
echo "Installing krabssyd service..."
cp /usr/bin/python3 /usr/bin/krabssydpy
cp /usr/bin/python3.6 /usr/bin/krabssydpy
cp ./krabssy-installer-tmp/krabssyd.service /lib/systemd/system
systemctl daemon-reload

clear
echo "Installing pip..."
curl https://bootstrap.pypa.io/get-pip.py -o ./krabssy-installer-tmp/get-pip.py
krabssydpy ./krabssy-installer-tmp/get-pip.py

clear
echo "Installing required Python modules..."
krabssydpy -m pip install -r ./krabssy-installer-tmp/requirements.txt

clear
echo "Removing temporary files..."
rm -rf ./krabssy-installer-tmp/