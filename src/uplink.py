
import time
import os

from picamera import PiCamera
from datetime import datetime

from gpiozero import LED
GPIO_PIN=27

# Camera - take a picture
def camera():
    os.chdir("~/FLIGHT_DATA_S23/PICTURES/")

    camera = PiCamera()
    fname = datetime.now().strftime("%H-%M-%S") + ".jpg"
    camera.start_preview()
    camera.capture(fname)
    camera.stop_preview()

    os.chdir("~")

    out = "pic: " + fname + "\n"
    print(out)
    return out

# TODO: Cutdown function w/ nichrome test
def cutdown():
    print("Cutdown activated")
    pin = LED(GPIO_PIN)
    pin.on()
    time.sleep(4)
    pin.off()

monitor_file_path = "~/FLIGHT_DATA_S23/flight_output.txt"

def checkOutputFile():
    file = open(os.path.expanduser(monitor_file_path), "r")
    fileContent = file.readlines()
    file.close()

    # splitFileContent = fileContent.split("\n")
    lastTenLines = fileContent[-10:]
    lastTenLinesString = "\n".join(lastTenLines)


    searchString = "cutdown" + datetime.now().strftime("%H-%M")

    if searchString in lastTenLinesString:
        print("Activating Cutdown")

        try:
            with open("flight_log.txt", "a+") as subfile:
                subfile.write(cutdown())
            subfile.close()
        except:
            print("Cutdown Error")

    if "picture" in lastTenLinesString:
        print("Taking Picture")

        try:
            with open("flight_log.txt", "a+") as subfile:
                subfile.write(camera())
            subfile.close()
        except:
            print("Picture Error")

while True:
    try:
        checkOutputFile()
    except:
        print("Error checking uplink")
    time.sleep(5)