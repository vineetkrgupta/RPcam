import datetime as dt
from flask import send_file
from picamera import PiCamera
from time import sleep
from datetime import datetime
import subprocess
from subprocess import call
from time import sleep
from fractions import Fraction
import psutil
import os
last = "x"

cwd = os.getcwd()


iso = 0 # 0 is for default other options being 1

# start the ffmpeg process with a pipe for stdin
# I'm just copying to a file, but you could stream to somewhere else
def ff(timestamp):
    global last
    last =cwd+'/static/Videos/Video_{}.h264'.format(timestamp)
    ffmpeg = subprocess.Popen([
        'ffmpeg', '-i', '-',
        '-vcodec', 'copy',
        '-an', last,
        ], stdin=subprocess.PIPE)
    return ffmpeg

from flask import Flask
app = Flask(__name__)


camera = PiCamera()
frames = camera.framerate
@app.route('/')
def hello_word():
    return 'Camera control ready'

#add a function to capture  image after certain amount of time or something like that idk 
    #add suppport for motion pir sensor and stuff
@app.route('/StartRecord')
def start_record():
    global camera
    global iso
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    camera.resolution = (1296, 972)
    camera.framerate=30
    camera.iso = iso 
    camera.rotation = 180
    camera.awb_mode='auto'
    camera.video_stabilization= True
    x = ff(timestamp)
    #x.stdin
    camera.start_recording(cwd+'/static/Videos/Video_{}.h264'.format(timestamp), format='h264', bitrate=20000000 ) #quality 1-40 dont mention 

    return 'Camera recording...'

@app.route('/StopRecord')
def stop_record():
    global camera
    camera.stop_recording()
    return 'Camera video stopped!'

@app.route('/TakePicture')
def take_picture():
    global camera
    global last 
    global iso 
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    camera.framerate = frames
    #camera.shutter_speed = camera.exposure_speed
    camera.resolution = (2592, 1944)
    camera.rotation = 180
    camera.iso = iso
    camera.capture(cwd+'/static/Pictures/Photo_{}.jpg'.format(timestamp))
    last = cwd+'/static/Pictures/Photo_{}.jpg'.format(timestamp)
    return 'Camera photo captured!'

@app.route('/TakePicNight')
def take_picNight():
    global camera
    global last
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    camera.framerate = Fraction(1, 4)
    camera.shutter_speed = 4000000
    camera.exposure_mode = 'off'
    camera.iso = 800
    camera.resolution = (1296, 972)
    camera.rotation = 180
    camera.capture(cwd+'/static/Pictures/NightPhoto_{}.jpg'.format(timestamp))
    last = cwd+'/static/Pictures/NightPhoto_{}.jpg'.format(timestamp)
    return 'Night Camera photo captured!'



@app.route('/StartLive')
def start_live():
    global camera
    camera.preview_fullscreen=False
    camera.resolution =(944, 600)
    camera.rotation = 180
    camera.preview_window=(0,0,944,600)
    preview = camera.start_preview()
    return 'Camera start live!'

@app.route('/StopLive')
def stop_live():
    global camera
    camera.stop_preview()
    return 'Camera stop live!'

@app.route('/check')
def check():
    path = '/'
    bytes_avail = psutil.disk_usage(path).free
    gigabytes_avail = bytes_avail / 1024 / 1024 / 1024
    return (str(gigabytes_avail)+'GB left ')

@app.route('/day')
def day():
    global iso 
    iso = 100
    return 'Set to Day'

@app.route('/night')
def night():
    global iso
    iso = 800
    return 'Set to Night '

@app.route('/auto')
def auto():
    global iso
    iso = 0
    return 'Set to auto'

@app.route('/shutdown')
def shutdown():
    call("sudo shutdown -h now", shell=True)
@app.route('/last')
def last():
    global last
    try:
        return send_file(last)
    except:
        return("No last file in record")

if __name__ == '__main__':
    app.run(host='0.0.0.0')