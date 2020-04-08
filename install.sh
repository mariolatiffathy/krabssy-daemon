!/bin/bash
echo "FabitManage Daemon v1.0-alpha Installer"
echo "==========================================="
echo "Downloading components..."
git clone https://github.com/mariolatiffathy/fabitmanage-daemon.git fabitmanage-installer-tmp
mkdir -p /fabitmanage-daemon && cp ./fabitmanage-installer-tmp/daemon.py /fabitmanage-daemon
mkdir -p /fabitmanage-daemon/config && cp ./fabitmanage-installer-tmp/config/daemon.ini /fabitmanage-daemon/config
echo "Removing temporary files..."
rm -rf ./fabitmanage-installer-tmp/