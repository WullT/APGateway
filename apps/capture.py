# https://fhnw.mit-license.org/

import requests
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import datetime
import shutil
import sqliteadapter
from dataclasses import dataclass

check_interval = 5 # seconds to wait before checking again


@dataclass
class Camera:
    id: str
    url: str
    interval: int
    username: str
    password: str
    timestamp: datetime.datetime
    record_start_hour: int
    record_start_minute: int
    record_stop_hour: int
    record_stop_minute: int
    enabled: int


data_dir = sqliteadapter.get_data_dir()


if not os.path.exists(data_dir):
    os.makedirs(data_dir)


def get_cameras():
    cameras = []

    cams = sqliteadapter.get_cameras()
    for camera in cams:
        c = Camera(
            camera[0],
            camera[1],
            camera[2],
            camera[3],
            camera[4],
            camera[5],
            camera[6],
            camera[7],
            camera[8],
            camera[9],
            camera[10],
        )
        if c.timestamp == None:
            sqliteadapter.update_timestamp(c.id, datetime.datetime.utcnow())
        cameras.append(c)
    return cameras


cameras = get_cameras()


def cam_ready(cam: Camera):
    if cam.enabled == 1:
        utc_time = datetime.datetime.utcnow()
        time_until_start = (
            cam.record_start_hour * 60
            + cam.record_start_minute
            - utc_time.hour * 60
            - utc_time.minute
        )
        time_until_stop = (
            cam.record_stop_hour * 60
            + cam.record_stop_minute
            - utc_time.hour * 60
            - utc_time.minute
        )
        if (time_until_start <= 0) and (time_until_stop >= 0):
            if (cam.timestamp + datetime.timedelta(seconds=cam.interval)) <= utc_time:
                return True
    return False


def capture_from(cam: Camera):
    if not cam_ready(cam):
        return None
    url = cam.url
    print(url)
    utc_time = datetime.datetime.utcnow()
    sqliteadapter.update_timestamp(cam.id, utc_time)
    filename = cam.id + "_" + utc_time.strftime("%Y-%m-%dT%H-%M-%SZ") + ".jpg"
    savepath = (
        data_dir
        + "/"
        + cam.id
        + "/"
        + utc_time.strftime("%Y-%m-%d")
        + "/"
        + utc_time.strftime("%H")
        + "/"
        + filename
    )
    try:
        os.makedirs(
            os.path.dirname(savepath), exist_ok=True
        )  # create path if not exists
        r = requests.get(
            url, stream=True, auth=HTTPBasicAuth(cam.username, cam.password)
        )
        # print("Camera",camera_id,": status code=", r.status_code)
        if r.status_code == 200:
            with open(savepath, "wb") as out_file:
                shutil.copyfileobj(r.raw, out_file)
            sqliteadapter.update_status_code(cam.id, r.status_code)
        else:
            print("Failed. Status code", r.status_code)
            sqliteadapter.update_status_code(cam.id, r.status_code)
        return cam.id + " : " + str(r.status_code)
    except Exception as e:
        print(e)
        print("setting status code to 408")
        sqliteadapter.update_status_code(cam.id, 408)


def capture_all():
    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for camera in cameras:
            futures.append(executor.submit(capture_from, camera))

    for future in as_completed(futures):
        if not future.result() == None:
            print(future.result())


while True:
    t0 = time.time()
    cameras = get_cameras()
    data_dir = sqliteadapter.get_data_dir()
    capture_all()
    d = time.time() - t0
    if d < check_interval:
        time.sleep(check_interval - d)
