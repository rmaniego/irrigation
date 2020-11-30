try:
    import Adafruit_DHT
    import RPi.GPIO as GPIO
    from urllib import request
    from time import sleep, strftime
    from arkivist import Arkivist
except:
    print("Some required packages are not yet installed.")
    print("Requires: Adafruit_DHT, urllib, time, RPi, arkivist")
    import sys
    sys.exit(1)

def irrigation():
    # get your api key first
    # https://home.openweathermap.org/api_keys
    key = "enter_your_api_key_here"
    # find your coordinates
    # https://www.latlong.net/
    longitude = ""
    latitude = ""
    weather = Arkivist("weather.json")
    
    try:
        # GPIO setup
        RELAIS_1_GPIO = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAIS_1_GPIO, GPIO.OUT)

        # custom settings
        has_irrigated = False
        irrigation_time = 15 * 60 # 15 minutes
        irrigation_time = 5
        irrigation_rest = 60 * 60 # 60 minutes
        irrigation_rest = 5
        
        # infinite loop
        while (True):
            current_hour = int(strftime("%H"))
            print(f"Hour: {current_hour}")
            ## turn off water pump as default
            GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
            if 6 <= current_hour <= 10:
                ## best irrigation time is between 6 AM - 10 AM
                if not has_irrigated:
                    # check weather api first
                    weather.load(weatherman(latitude, longitude, key))
                    weather.flatten()
                    temp = weather.search("main.temp", None)
                    humidity = weather.search("main.humidity", None)
                    if humidity == None or temp == None:
                        # if weather api is unavailable, use sensors
                        print(" - ApiError: Check your internet connection...")
                        ## GPIO number = 4, check in actual
                        ## the sensors are only ready every two seconds.
                        ## be careful not to start a query every second.
                        humidity, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
                        pass
                    if humidity is not None or temp is not None:
                        ## continue if values are valid
                        print(f" - Humidity: {humidity}, Temperature: {temp}")
                        if int(humidity) <= 90 and int(temp) >= 25:
                            ## humidity when it rains is about 100%
                            ## temperature when it rains is about ~27C (25C for testing)
                            ## turn on water pump
                            print(" - WaterPump: Powering on...")
                            GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
                            
                            print(" - WaterPump: Irrigation started.")
                            sleep(irrigation_time)
                            
                            print(" - WaterPump: Powering off...")
                            GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
                            print(" - WaterPump: Irrigation ended.")
                            has_irrigated = True
                    else:
                        print(" - SensorError: Please check DHT sensor...")
            if has_irrigated and current_hour > 10:
                # reset irrigation flag after irrigation hours
                print(" - IrrigationFlag: Restored.")
                has_irrigated = False
            print(" - Sleeping...")
            sleep(irrigation_rest)
    except:
        print("Code might be broken, undo some of your changes...")

def weatherman(lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?units=metric&lat={lat}&lon={lon}&appid={key}"
        with request.urlopen(url) as source:
            return source.read().decode()
    except:
        return {}

irrigation()