# mobile-logger
Files to be installed on RPi+MC7455 for data collection

qmicapturegps.py - main python code to capture, store and transmit gps and signal data (invokes mmcli, qmicli)
raw-ip-wwan0.sh - workaround script to fix problem with qmi network utils not setting interface mode correctly
rawip.service - should run workaround when modem network interface comes up (before connection)
qmicapture.service - runs capture script after connection
4g.nmconnection - NetworkManager script for auto-connection
flashservice - started by NetworkManager when no network connection

Apart from python3, needs network-manager, wiringpi, mosquitto_clients and libqmi-utils packages
