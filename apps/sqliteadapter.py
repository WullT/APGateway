# https://fhnw.mit-license.org/

import sqlite3
import os
import datetime


default_data_dir = "/home/pi/captures"
default_interval = 15
default_username = "MY_USER"
default_password = "MY_PASSWORD"
default_port = 8080
default_action = "/?action=snapshot"
default_record_start_hour = 8
default_record_start_minute = 0
default_record_stop_hour = 18
default_record_stop_minute = 0
default_enabled = 1

db_dir = "/home/pi/config"
db_path = db_dir + "/camera_info.db"
if not os.path.exists(db_dir):
    os.makedirs(db_dir)


con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS cameras
               (id text UNIQUE, 
               url text, 
               interval int, 
               username text, 
               password text, 
               Timestamp TIMESTAMP, 
               record_start_hour int, 
               record_start_minute int, 
               record_stop_hour int, 
               record_stop_minute int, 
               enabled int, 
               status_code int)"""
)
cur.execute(
    """CREATE TABLE IF NOT EXISTS default_values
               (port int, 
               action text, 
               interval int, 
               username text, 
               password text, 
               record_start_hour int, 
               record_start_minute int, 
               record_stop_hour int, 
               record_stop_minute int, 
               enabled int)"""
)
cur.execute(
    """CREATE TABLE IF NOT EXISTS global_config
               (data_dir text UNIQUE)"""
)
cur.execute("""SELECT * FROM default_values""")
default_values = cur.fetchall()
if len(default_values) == 0:
    cur.execute(
        """INSERT INTO default_values VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            default_port,
            default_action,
            default_interval,
            default_username,
            default_password,
            default_record_start_hour,
            default_record_start_minute,
            default_record_stop_hour,
            default_record_stop_minute,
            default_enabled,
        ),
    )
    con.commit()
else:
    default_port = default_values[0][0]
    default_action = default_values[0][1]
    default_interval = default_values[0][2]
    default_username = default_values[0][3]
    default_password = default_values[0][4]
    default_record_start_hour = default_values[0][5]
    default_record_start_minute = default_values[0][6]
    default_record_stop_hour = default_values[0][7]
    default_record_stop_minute = default_values[0][8]
    default_enabled = default_values[0][9]

cur.execute("""INSERT OR IGNORE INTO global_config VALUES (?)""", (default_data_dir,))
con.commit()
cur.close()
con.close()


def hm2timeString(hour, minute):
    if hour < 10:
        hour = "0" + str(hour)
    else:
        hour = str(hour)
    if minute < 10:
        minute = "0" + str(minute)
    else:
        minute = str(minute)
    return hour + ":" + minute


def get_default_values():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""SELECT * FROM default_values""")
    rows = cur.fetchall()
    cur.close()
    con.close()
    return rows[0]


def state2enabled(state):
    if state == 1:
        return "Enabled"
    else:
        return "Disabled"


def state2checked(state):
    if state == 1:
        return "checked"
    else:
        return ""


def get_default_values_json():
    defvals = get_default_values()
    defvals_json = {
        "port": defvals[0],
        "action": defvals[1],
        "interval": defvals[2],
        "username": defvals[3],
        "password": defvals[4],
        "record_start_hour": defvals[5],
        "record_start_minute": defvals[6],
        "record_stop_hour": defvals[7],
        "record_stop_minute": defvals[8],
        "enabled": defvals[9],
    }
    defvals_json["record_start_time"] = hm2timeString(
        defvals_json["record_start_hour"], defvals_json["record_start_minute"]
    )
    defvals_json["record_stop_time"] = hm2timeString(
        defvals_json["record_stop_hour"], defvals_json["record_stop_minute"]
    )
    defvals_json["state_c"] = state2checked(defvals_json["enabled"])
    return defvals_json


def add_new_camera(camera_id):
    default_values = get_default_values_json()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    dev_id = camera_id.split("cam-")[1]
    url = "http://" + camera_id + ".local:"+str(default_values["port"])+default_values["action"]
    cur.execute(
        """INSERT OR IGNORE INTO cameras VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)""",
        (
            dev_id,
            url,
            default_values["interval"],
            default_values["username"],
            default_values["password"],
            datetime.datetime.utcnow(),
            default_values["record_start_hour"],
            default_values["record_start_minute"],
            default_values["record_stop_hour"],
            default_values["record_stop_minute"],
            default_values["enabled"],
            None,
        ),
    )
    con.commit()
    cur.close()
    con.close()


def get_cameras():
    con = sqlite3.connect(
        db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    cur = con.cursor()
    cur.execute("""SELECT * FROM cameras""")
    rows = cur.fetchall()
    cur.close()
    con.close()
    return rows


def get_camera(id):
    con = sqlite3.connect(
        db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    cur = con.cursor()
    cur.execute("""SELECT * FROM cameras WHERE id = ?""", (id,))
    rows = cur.fetchall()
    cur.close()
    con.close()
    return rows[0]


def get_camera_json(id):
    cam = get_camera(id)

    return dbCam2json(cam)


def get_cameras_json():
    cams = get_cameras()
    cameras = []
    for cam in cams:
        cameras.append(dbCam2json(cam))
    return cameras


def dbCam2json(cam):
    cam_json = {
        "id": cam[0],
        "url": cam[1],
        "interval": cam[2],
        "username": cam[3],
        "password": cam[4],
        "last_update": cam[5],
        "record_start_hour": cam[6],
        "record_start_minute": cam[7],
        "record_stop_hour": cam[8],
        "record_stop_minute": cam[9],
        "enabled": cam[10],
        "status_code": cam[11],
    }
    cam_json["record_start_time"] = hm2timeString(
        cam_json["record_start_hour"], cam_json["record_start_minute"]
    )
    cam_json["record_stop_time"] = hm2timeString(
        cam_json["record_stop_hour"], cam_json["record_stop_minute"]
    )
    cam_json["state_c"] = state2checked(cam_json["enabled"])

    cam_json["state"] = state2enabled(cam_json["enabled"])
    cam_json["last_update"] = cam[5].strftime("%d.%m.%Y %H:%M:%S")
    if cam_json["status_code"] == 200:
        cam_json["status_class"] = "bg-success"
    else:
        cam_json["status_class"] = "bg-danger"
    return cam_json


def update_status_code(camera_id, status_code):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """UPDATE cameras SET status_code = ? WHERE id = ?""", (status_code, camera_id)
    )
    con.commit()
    cur.close()
    con.close()


def update_timestamp(camera_id, new_time):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """UPDATE cameras SET Timestamp = ? WHERE id = ?""",
        (
            new_time,
            camera_id,
        ),
    )
    con.commit()
    cur.close()
    con.close()


def get_data_dir():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""SELECT * FROM global_config""")
    rows = cur.fetchall()
    cur.close()
    con.close()
    return rows[0][0]


def update_camera_config(
    camera_id,
    url,
    interval,
    username,
    password,
    record_start_hour,
    record_start_minute,
    record_stop_hour,
    record_stop_minute,
    enabled,
):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """UPDATE cameras SET 
        url = ?, 
        interval = ?, 
        username = ?, 
        password = ?, 
        record_start_hour = ?, 
        record_start_minute = ?, 
        record_stop_hour = ?, 
        record_stop_minute = ?, 
        enabled = ? 
        WHERE id = ?""",
        (
            url,
            interval,
            username,
            password,
            record_start_hour,
            record_start_minute,
            record_stop_hour,
            record_stop_minute,
            enabled,
            camera_id,
        ),
    )
    con.commit()
    con.close()


def update_global_config(data_dir):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""UPDATE global_config SET data_dir = ?""", (data_dir,))
    con.commit()
    cur.close()
    con.close()


def update_default_config(
    interval,
    username,
    password,
    record_start_hour,
    record_start_minute,
    record_stop_hour,
    record_stop_minute,
    enabled,
):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """UPDATE default_values SET 
        interval = ?,
        username = ?, 
        password = ?, 
        record_start_hour = ?, 
        record_start_minute = ?, 
        record_stop_hour = ?, 
        record_stop_minute = ?, 
        enabled = ?""",
        (
            interval,
            username,
            password,
            record_start_hour,
            record_start_minute,
            record_stop_hour,
            record_stop_minute,
            enabled,
        ),
    )
    con.commit()
    cur.close()
    con.close()


def remove_camera(camera_id):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""DELETE FROM cameras WHERE id = ?""", (camera_id,))
    con.commit()
    cur.close()
    con.close()
