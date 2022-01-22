# https://fhnw.mit-license.org/

from flask import Flask, request, render_template, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import sqliteadapter
from werkzeug.security import generate_password_hash, check_password_hash
import argparse
import os
import shutil

capture_svc_name = "capture.service"
registrationserver_svc_name = "registrationserver.service"

parser = argparse.ArgumentParser(description="APGateway Configuration Server")
parser.add_argument("--user", "-u", type=str, help="basic auth username", required=True)
parser.add_argument(
    "--password", "-p", type=str, help="basic auth password", required=True
)
parser.add_argument("--port", "-P", type=int, default=8080, help="port to listen on")

args = parser.parse_args()

BASIC_AUTH_PASSWORD = args.password
BASIC_AUTH_USER = args.user
PORT = args.port


users = {BASIC_AUTH_USER: generate_password_hash(str(BASIC_AUTH_PASSWORD))}

# simple web server
app = Flask(__name__)
auth = HTTPBasicAuth()

cameras = sqliteadapter.get_cameras_json()


def get_states():
    states = {}
    if os.system("systemctl is-active --quiet " + capture_svc_name) == 0:
        states["capture"] = "running"
        states["capture_category"] = "success"
    else:
        states["capture"] = "stopped"
        states["capture_category"] = "danger"
    if os.system("systemctl is-active --quiet " + registrationserver_svc_name) == 0:
        states["registrationserver"] = "running"
        states["registrationserver_category"] = "success"
    else:
        states["registrationserver"] = "stopped"
        states["registrationserver_category"] = "danger"
    try:
        total, used, free = shutil.disk_usage(sqliteadapter.get_data_dir())
        # total, used, free = shutil.disk_usage("/")
        total_gb = round(total / (1024 ** 3), 2)
        percent = round(used / total * 100, 2)
        if percent > 90:
            states["data_category"] = "danger"
        elif percent > 80:
            states["data_category"] = "warning"
        else:
            states["data_category"] = "success"
        states["disk_usage"] = str(percent) + " %"
        states["disk_total"] = str(total_gb) + " GB"
    except:
        states["disk_usage"] = "unknown"
        states["disk_total"] = "unknown"
        states["data_category"] = "warning"

    return states


def updateCamera(id, req):
    url = req["url"]
    username = req["username"]
    password = req["password"]
    interval = req["interval"]
    record_start = req["record_start"]
    record_stop = req["record_stop"]
    if "enabled" in req:
        enabled = 1
    else:
        enabled = 0
    record_start_hour = int(record_start.split(":")[0])
    record_start_minute = int(record_start.split(":")[1])
    record_stop_hour = int(record_stop.split(":")[0])
    record_stop_minute = int(record_stop.split(":")[1])
    sqliteadapter.update_camera_config(
        id,
        url,
        interval,
        username,
        password,
        record_start_hour,
        record_start_minute,
        record_stop_hour,
        record_stop_minute,
        enabled,
    )


def addCamera(req):
    dev_id = req["cam_id"]
    url = req["url"]
    username = req["username"]
    password = req["password"]
    sqliteadapter.add_camera_manual(dev_id, url, username, password)


def updateGlobalConfig(req):
    data_dir = req["data_dir"]
    sqliteadapter.update_global_config(data_dir)


def updateDefaultValues(req):
    interval = req["interval"]
    username = req["username"]
    password = req["password"]
    record_start = req["record_start_time"]
    record_stop = req["record_stop_time"]
    if "enabled" in req:
        enabled = 1
    else:
        enabled = 0
    record_start_hour = int(record_start.split(":")[0])
    record_start_minute = int(record_start.split(":")[1])
    record_stop_hour = int(record_stop.split(":")[0])
    record_stop_minute = int(record_stop.split(":")[1])
    sqliteadapter.update_default_config(
        interval,
        username,
        password,
        record_start_hour,
        record_start_minute,
        record_stop_hour,
        record_stop_minute,
        enabled,
    )


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route("/")
@auth.login_required
def index():
    cameras = sqliteadapter.get_cameras_json()
    return render_template("index.html", content=cameras, states=get_states())


@app.route("/global", methods=["GET", "POST"])
@auth.login_required
def globalsettings():
    if request.method == "GET":
        default_values = sqliteadapter.get_default_values_json()
        return render_template(
            "defaultconfig.html",
            glob=default_values,
            data_dir=sqliteadapter.get_data_dir(),
        )
    else:
        req = request.form
        updateDefaultValues(req)
        updateGlobalConfig(req)
        return redirect(url_for("index"))


@app.route("/camera/<cameraid>/edit", methods=["GET", "POST"])
@auth.login_required
def camera(cameraid):
    if request.method == "GET":
        cam = sqliteadapter.get_camera_json(cameraid)
        return render_template("camera.html", cam=cam)
    else:
        req = request.form
        updateCamera(cameraid, req)
        return redirect(url_for("index"))


@app.route("/camera/add", methods=["GET", "POST"])
@auth.login_required
def add_camera():
    if request.method == "GET":
        default_values = sqliteadapter.get_default_values_json()
        return render_template("addcamera.html", dv=default_values)
    else:
        req = request.form
        addCamera(req)
        return redirect(url_for("index"))


@app.route("/camera/<cameraid>/remove", methods=["GET"])
@auth.login_required
def removeCamera(cameraid):

    sqliteadapter.remove_camera(cameraid)
    return redirect(url_for("index"))


if "__main__" == __name__:
    app.run(host="0.0.0.0", port=PORT, debug=False)
