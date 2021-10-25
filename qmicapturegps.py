# capture radio and gps data from mc7455 modem (in QMI mode)
# (need qmi to get cell info which isn't available in mbim mode)
# store data as local csv and also send mqtt 
# Stephen Tickell, EMS

import subprocess
import time
import os
from datetime import datetime

# get modem mac address for uuid
try:
    tempFile = open( "/sys/class/net/eth0/address" )
    gwmac = tempFile.read().strip()
    tempFile.close()
except:
    try:
        tempFile = open( "/sys/class/net/eno1/address" )
        gwmac = tempFile.read().strip()
        tempFile.close()
    except:
        gwmac = "001122334455"

# get imei
try:
    imei = subprocess.check_output("sudo mmcli -m 0", shell=True).decode("ascii").split("imei: ")[1].split()[0]
except:
    imei = "dummyIMEI"
    
# static parameters, in format required for csv and mqtt    
fdata = "{},{}".format(gwmac, imei)
fstr = "\"uuid\":\"{}\", \"hw_info\" : \"MC7455\", \"imei\" : \"{}\", \"network\" : \"3\"  ".format(gwmac, imei)
print(fdata)

# start a new capture file
try:
    fd = open("/home/pi/capture/radio-{}.csv".format(datetime.now().strftime("%Y-%m-%d-%H%M")), "w")
    fd.write("date, time, uuid, imei, longitude, latitude, RSSI, RSRQ, RSRP, SNR, tac, cellid\n")
except Exception as e:
    print(e)
    
while True:
    lng = 0
    lat = 0
    sigargs = ['','','',''] 
    locstr = ""
    sigstr = ""
    cellstr = ""
    cellid=""
    tac=""
    try:
# should only need to run this once, but doesn't always work first time        
        subprocess.run("sudo mmcli -m 0 --location-enable-gps-raw", shell=True)
#        tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
#        cpu_temp = tempFile.read()
#        tempFile.close()
        gpsraw = subprocess.check_output("sudo mmcli -m 0 --location-get", shell=True).decode("ascii")
#        print(gpsraw)
        lng = gpsraw.split("longitude: ")[1].split()[0]
        lat = gpsraw.split("latitude: ")[1].split()[0]
        locstr = ", \"location\" : \"{}, {}\" ".format(lat,lng)
# flash status led if gps available        
        subprocess.run("gpio write 7 1",shell=True)
        time.sleep(0.3)
        subprocess.run("gpio write 7 0",shell=True)
    except Exception as e:
        print(e)
# get signal info and parse the bits we need
    try:
        siginfo = subprocess.check_output("sudo qmicli -p -d /dev/cdc-wdm0 --nas-get-signal-info", shell=True).decode("ascii").split('LTE:')[1].split()
        sigargs = [v[1:] for v in siginfo[1::3]]
        sigstr = ", \"RSSI\" : {}, \"RSRQ\" : {}, \"RSRP\" : {}, \"SNR\" : {} ".format(*sigargs)
 #       print(sigargs)
    except Exception as e:
        print(e)
        
# get cell info
    try:
#        print(lng+" "+lat)
#        print("{},{}".format(datetime.now().isoformat(timespec='seconds'),','.join(v[1:] for v in s[1::3])))
#        fd.write("\"{}\",{},{},{} ".format(datetime.now().strftime("%b %d, %Y @ %H:%M:%S"), lng, lat,','.join(v[1:] for v in s[1::3])))
        cell = subprocess.check_output("sudo qmicli -p -d /dev/cdc-wdm0 --nas-get-cell-location-info", shell=True).decode("ascii")
#        print(cell)
        tac = cell.split('Tracking Area Code:')[1].split()[0].strip("'")
        cellid = cell.split('Global Cell ID:')[1].split()[0].strip("'")
        cellstr = ", \"tac\" : \"{}\", \"cellid\" : \"{}\" ".format(tac, cellid)
    except Exception as e:
        print(e)
        
    try:        
        fd.write("{},{},{},{},{} ".format(datetime.now().strftime("%D, %H:%M:%S"), fdata, lng, lat,','.join(sigargs)))
        fd.write(",{},{}".format(tac, cellid))
        fd.write("\n")
# not sure if this is needed, and probably increases wear+tear on pi sdcard
#        fd.flush()

        msg = "{{ {} {} {} {} }}".format(fstr, locstr, cellstr, sigstr)
        print(msg)
        subprocess.run(["mosquitto_pub", "-h", "test.mosquitto.org", "-t", "ems/radiodata", "-m", msg])        
#        matchlist = [s for s in simstatus.split() if '8944' in s]
#        if len(matchlist) > 0:
#            mysim = matchlist[0].strip("'")
    except Exception as e:
        print(e)
# loop time
    time.sleep(10)
#    print('loop')

