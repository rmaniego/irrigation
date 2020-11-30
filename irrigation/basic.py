import Adafruit_DHT
import RPi.GPIO as GPIO
from time import sleep, strftime

# GPIO setup
RELAIS_1_GPIO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT)

# custom settings
has_irrigated = False
irrigation_time = 15 * 60 # 15 minutes
irrigation_rest = 60 * 60 # 60 minutes

## infinite loop
while (True):
    current_hour = int(strftime("%H"))
    print(f"Hour: {current_hour}")
    ## turn off water pump as default
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    if 6 <= current_hour <= 10:
        ## best irrigation time is between 6 AM - 10 AM
        if not has_irrigated:
            ## GPIO number = 4, check in actual
            ## the sensors are only ready every two seconds.
            ## be careful not to start a query every second.
            humidity, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
            if humidity is not None and temp is not None:
                ## continue if values are valid
                print(f" - Humidity: {humidity}, Temperature: {temp}")
                if int(humidity) <= 90 and int(temp) > 27:
                    ## humidity when it rains is about 100%
                    ## temperature when it rains is about 27C
                    ## turn on water pump
                    print(" - WaterPump: Powering on...")
                    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
                    
                    print(" - WaterPump: Irrigating started.")
                    sleep(irrigation_time)
                    
                    print(" - WaterPump: Powering off...")
                    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
                    print(" - WaterPump: Irrigating ended.")
                    has_irrigated = True
            else:
                print(" - SensorError: Please check DHT sensor...")
    if has_irrigated and current_hour > 10:
        # reset irrigation flag after irrigation hours
        print(" - IrrigationFlag: Restored.")
        has_irrigated = False
    print(" - Sleeping...")
    sleep(irrigation_rest)