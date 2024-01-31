import board
import sys
from os import getenv
from time import sleep
from adafruit_dht import DHT22
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Handle arguments. First argument is the name of the influxdb point and the second is the tag to be used
if (len(sys.argv) < 3):
    print("No name or tag specified in the arguments")
    sys.exit()
NAME = sys.argv[1]
TAG = sys.argv[2]

# Setup influx database
load_dotenv()
INFLUX_TOKEN = getenv("INFLUX_TOKEN")
ORG = getenv("ORG")
URL = getenv("URL")
bucket="dht"
write_client = InfluxDBClient(url=URL, token=INFLUX_TOKEN, org=ORG)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

# Sensor data pin is connected to GPIO 4
sensor = DHT22(board.D4)

while True:
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        humidity = sensor.humidity
        print("Temp={0:0.1f}ºC, Humidity={1:0.1f}%".format(temperature_c, humidity))
        write_api.write(bucket, ORG, record=(
            Point(NAME)
            .tag("location", TAG)
            .field("temp", temperature_c)
            .field("humidity", humidity)
        ))

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
    except Exception as error:
        sensor.exit()
        raise error

    sleep(3.0)