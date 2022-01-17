# https://fhnw.mit-license.org/

from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import os
import requests
import sqliteadapter
import time

info_port = 8000
max_workers = 127
discovery_scan_interval = 60


def get_base_addr(interface):
    gw = os.popen("ip -4 route show dev " + interface).read().split()
    if len(gw) == 0:
        return None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    addr = s.getsockname()[0].split(".")
    s.close()
    addr = addr[0] + "." + addr[1] + "." + addr[2] + "."
    return addr


found_cams = []


def scan_port(ip):
    socket.setdefaulttimeout(1)
    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = socket_obj.connect_ex((ip, info_port))
    if res == 0:
        print("Port", info_port, "is open on", ip)
        socket_obj.close()
        found_cams.append(ip)
        return True
    else:
        socket_obj.close()
        return False


def scan_if(interface):
    base_addr = get_base_addr(interface)
    if base_addr:
        print("scanning", interface, "with base address", base_addr)
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for ip_4 in range(1, 255):
                ip = base_addr + str(ip_4)
                futures.append(executor.submit(scan_port, ip))


def handle_results():
    for ip in found_cams:
        ans = requests.get("http://" + ip + ":" + str(info_port))
        try:
            cam_info = ans.json()
            hostname = cam_info["hostname"]
            print(hostname)
            sqliteadapter.add_new_camera(hostname)
        except:
            print("Error finding hostname for:", ip)


while True:
    t0 = time.time()
    scan_if("eth0")
    scan_if("wlan0")
    handle_results()
    t1 = time.time()
    found_cams = []
    if t1 - t0 < discovery_scan_interval:
        time.sleep(discovery_scan_interval - (t1 - t0))
