#!/bin/bash
sleep 5
/usr/sbin/ifconfig wwan0 down
/usr/bin/qmicli -d /dev/cdc-wdm0 --set-expected-data-format=raw-ip
/usr/sbin/ifconfig wwan0 up
/usr/bin/touch /tmp/rawip

