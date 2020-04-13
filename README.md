# FabitManage Daemon
The daemon handles all the messages sent from the panel, and it also sends messages to the panel.

# Dependencies used
- To be edited...

# Requirements
- Python 3.7.3
- cgroups v1

# Notes
- All the tests were done on Debian 10
- The FabitManage Daemon will override any cgroups configurations and rules on the system. So you can't use the FabitManage Daemon with another thing that uses cgroups on the same system.