#!/bin/sh
rclocal="/etc/rc.local"
cat > $rclocal <<EOF
# Run MQTT Poller on boot
counter=0
while ! /sbin/ifconfig wlan0 | grep -q 'inet addr:[0-9]'; do
        counter=$((counter + 1))
        if [ $counter -gt 6 ]
        then
                break
        fi
    # Wait for WIFI connection
    sleep 3
    done
# Once the device has a WIFI connection it will begin to poll
sudo python3 /home/pi/smarthome/src/MQTT_Poller.py & > /home/pi/poller.txt 2>&1

exit 0
EOF
