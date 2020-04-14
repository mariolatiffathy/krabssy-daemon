# FabitManage Daemon
The daemon handles all the messages sent from the panel, and it also sends messages to the panel.

# Dependencies used
- To be edited...

# Requirements
- Python 3.7.3 or 3.6.X
- cgroups v1

# Installation
1. Execute `install.sh` using `sh install.sh`

2. Edit `/etc/fstab` and add `usrquota,grpquota` options for the `/home` partition.

3. Enable the quota by typing:
```
mount -o remount /home

quotacheck -cugv /home

quotaon /home/
```

4. **If you are on Debian/Ubuntu:** Edit `/etc/default/grub` and the add `cgroup_enable=memory swapaccount=1` parameters to `GRUB_CMDLINE_LINUX_DEFAULT`. After that, type `update-grub` then reboot the system.

5. to complete... (create db, import sql, edit daemon configuration file, and start the fabitmanaged service)

# Notes
- All the tests were done on Debian 10
- The FabitManage Daemon will override any cgroups configurations and rules on the system. So you can't use the FabitManage Daemon with another thing that uses cgroups on the same system.