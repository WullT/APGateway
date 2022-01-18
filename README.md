# APGateway

Consists of

* [discover](apps/discover.py), an application that scans all network interfaces for [PoECams](https://github.com/WullT/PoECam)
* [capture](apps/capture.py), an application that downloads captures from the connected cameras
* [configserver](apps/configserver.py), a local http server to configure the system

## Setup

### Write Raspberry Pi OS to an SD card

- Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and run it
- Select *OS &rarr; Raspberry Pi OS (other) &rarr; Raspberry Pi OS Lite*
- Click `CTRL + SHIFT + X` to enter advanced options
- Check the button next to `enable SSH`
- Set an SSH password
- Enter Wifi credentials (best is a smartphone hotspot) and set the WiFi-country
- Click Save
- Select your SD card
- Click Write

### Access the Raspberry Pi

- Insert the SD card into the Raspberry Pi
- Plug in the power supply
- If you are using a smartphone hotspot, you will see a connected device and its ip
- Open a cmd terminal and type `ssh pi@<raspberrypi_hostname>.local` , e.g.
```sh
ssh pi@raspberrypi.local
```
- enter your password
- If you have chosen a weak password, change the password with:
```sh
passwd
```

### Install the APGateway applications
```sh
curl https://raw.githubusercontent.com/WullT/APGateway/main/scripts/clone_install_add_services.sh | bash
```

### Change login credentials for [configserver](apps/configserver.py)

```sh
sudo nano /etc/systems/system/configserver.service
```
In line 10, change username (default `admin`) and password (default `CHANGE_ME`)

To apply changes, run
```sh
sudo systemctl restart configserver.service
```

### Mount a USB storage device

- format the USB stick / Harddisk to ntfs
- give it a name
- on the Raspberry Pi, create a new directory, e.g.
```sh
mkdir /mnt/usb
```
- edit `/etc/fstab`
```sh
sudo nano /etc/fstab
```
- append this line to the file, change LABEL=*data* to the name of your storage device.
```conf
LABEL=data /mnt/usb ntfs defaults,auto,users,rw,nofail,umask=000,x-systemd.device-timeout=30 0 0
```
- reboot the Raspberry Pi

### Static networks

Edit `/etc/network/interfaces`

Example with an additional interface (USB-ethernet dongle &rarr; `eth1`):
```conf
# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source /etc/network/interfaces.d/*

auto lo eth0 eth1 wlan0

allow-hotplug eth0
  iface eth0 inet dhcp

allow-hotplug eth1
 iface eth1 inet static
   address 192.168.50.1/24

allow-hotplug wlan0
 iface wlan0 inet dhcp
 wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
```

