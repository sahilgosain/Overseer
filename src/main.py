from time import sleep
import csv
from gpiozero import OutputDevice
from subprocess import Popen, PIPE, STDOUT

# geofence
import prediction as pred
import landing_prediction as land
from shapely.geometry import Point, Polygon


# removed asyncio - will run global connection in seperate terminal

# global data collection (json)
# json_cmd = "gpspipe -w | fgrep TPV > master.log"

# GLOBAL CONSTANTS
csv_cmd = "gpscsv -n 1 -f time,lat,lon,alt > output.csv"
run = True
MAX_ALT = 22000

# manual cutdown (endless signal)
def cutdown():
    pin = OutputDevice(4)
    pin.on()
    sleep(120)
    pin.off()
    run = False


# True if within redzone
def geofence(time, lat, lon, altitude):
    pred = pred.Predictor(22000, 1.0)
    zones = land.createZones()

    # check if at red zone
    def inZone(current):
        for shape in zones:
            if current.within(zones[shape]):
                return True
        return False

    # update predictor
    def update(c):
        pred.AddGPSPosition(c)
        return Point(pred.PreviousPosition["lat"], pred.PreviousPosition["lon"])
    
    # core output
    pos = {"time": time,
            "lat": lat,
            "lon": lon,
            "alt": altitude,
            "sats": pred.PreviousPosition["sats"],
            "fixtype": pred.PreviousPositon["fixtype"]
        }
    if inZone(update(pos)):
        return True
    else:
        return False

# position checking for cutdown
def main():
    while run:
        # load csv data
        ps = Popen(csv_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        output = ps.communicate()[0]
        # rotating data vals
        time, lat, lon, alt = (
            "",
            0.0,
            0.0,
            0.0
        )
        # csv parsing
        try:
            with open("output.csv", "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    time, lat, lon, alt = (
                        row[0],
                        float(row[1]),
                        float(row[2]),
                        float(row[3]),
                    )
        except:
            sleep(5)
        # call cutdown
        if alt >= MAX_ALT:
            cutdown()
        else:
            try:
                geofence(time, lat, lon, alt)
            except:
                continue
            finally:
                sleep(5)


# run
main()