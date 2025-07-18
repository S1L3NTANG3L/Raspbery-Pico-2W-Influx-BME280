import network
import ntptime
import time
from machine import *
import bme280_float as bme280
import requests
import gc

# Configuration
HOSTNAME = "WeatherPico2W"
INFLUXDB_URL = "http://ip:8086/api/v2/write?org=ORG&bucket=BUCKET&precision=s"
INFLUXDB_TOKEN = ""
HEADERS = {
    "Authorization": f"Token {INFLUXDB_TOKEN}",
    "Content-Type": "text/plain; charset=utf-8",
    "Accept": "application/json"
}
TIMEZONE_OFFSET = 2

# WiFi configuration
SSID = ""
PASSWORD = ""
RTC = RTC()
# Pin configuration
SDA_PIN = 16
SCL_PIN = 17
RAIN_SENSOR_PIN = 26

# Built-in LED
LED_PIN = Pin("LED", Pin.OUT)

def blink_led(times, delay=0.2):
    """Blink the built-in LED a specified number of times."""
    for _ in range(times):
        LED_PIN.on()  # Turn LED on
        time.sleep(delay)
        LED_PIN.off()  # Turn LED off
        time.sleep(delay)

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...")
    for _ in range(60):  # Try connecting for 10 seconds
        if wlan.isconnected():
            print("WiFi connected!")
            print("IP:", wlan.ifconfig()[0])
            blink_led(3, 0.1)  # Blink LED 3 times to indicate successful connection
            return wlan
        time.sleep(2)
    print("Failed to connect to WiFi.")
    blink_led(5, 0.1)  # Blink LED quickly 5 times for WiFi failure
    time.sleep(2)
    reset()  # Reboot the Pico

def ensure_wifi_connection(wlan):
    if not wlan.isconnected():
        print("WiFi disconnected. Reconnecting...")
        wlan.connect(SSID, PASSWORD)
        for _ in range(10):  # Try reconnecting for 10 seconds
            if wlan.isconnected():
                print("WiFi reconnected!")
                print("IP:", wlan.ifconfig()[0])
                blink_led(3, 0.1)  # Blink LED 3 times for reconnection
                return
            time.sleep(1)
        print("Failed to reconnect to WiFi.")
        blink_led(5, 0.1)  # Blink LED quickly 5 times for reconnection failure
        time.sleep(2)
        reset()  # Reboot the Pico

def sync_ntp_time():
    import ntptime
    ntptime.host = "za.pool.ntp.org"

    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"Attempting NTP time sync: {attempt + 1}/{max_retries}")
            ntptime.settime()
            print("Time synced successfully!")
            return
        except Exception as e:
            print(f"Failed to sync time on attempt {attempt + 1}: {e}")
            time.sleep(2)  # Retry after a short delay

    print("All retries failed. Cannot sync time.")
    blink_led(4, 0.3)  # Add error indication via LED
    time.sleep(2)
    reset()  # Reboot the Pico

def get_current_timestamp():
    timestamp = int(time.time())
    return timestamp

def get_sensor_data():
    i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)
    bme = bme280.BME280(i2c=i2c)
    temperature = float(bme.values[0])
    pressure = float(bme.values[1])
    humidity = float(bme.values[2])
    adc = ADC(Pin(RAIN_SENSOR_PIN))
    rain_value = adc.read_u16()
    return temperature, pressure, humidity, rain_value

def create_telemetry_data(temperature, pressure, humidity, rain_value, timestamp):
    telemetry_data = (
        f"Weather_Station,location=LOCATION "
        f"temperature={temperature},humidity={humidity},rain={rain_value},pressure={pressure} {timestamp}"
    )
    return telemetry_data

def send_to_influxdb(telemetry_data):
    print("Sending data to InfluxDB...")
    try:
        response = requests.post(INFLUXDB_URL, headers=HEADERS, data=telemetry_data)
        if response.status_code == 204:
            print("Data successfully sent to InfluxDB.")
            blink_led(1, 3)  # Blink LED once for successful data send
        else:
            print(f"Failed to send data: {response.status_code} - {response.text}")
            blink_led(4, 0.1)  # Blink LED quickly 4 times for send failure
        response.close()
    except Exception as e:
        print(f"Failed to send data: {e}")
        blink_led(4, 0.1)  # Blink LED quickly 4 times for request failure
        time.sleep(2) 
        reset()  # Reboot the Pico

def main():
    try:
        wlan = connect_to_wifi()
        sync_ntp_time()
        gc.enable()
        while True:
            ensure_wifi_connection(wlan) 
            timestamp = get_current_timestamp()
            temperature, pressure, humidity, rain_value = get_sensor_data()
            telemetry_data = create_telemetry_data(temperature, pressure, humidity, rain_value, timestamp)
            print("Telemetry Data:", telemetry_data)
            send_to_influxdb(telemetry_data)
            gc.collect()          
            print("Garbage collection completed.")
            blink_led(1, 1)  # Blink LED to indicate normal operation cycle
            for _ in range(30):  
                ensure_wifi_connection(wlan)
                time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")
        blink_led(6, 0.2)  # Blink LED dramatically for fatal errors
        time.sleep(2)  
        reset()  # Reboot the Pico

if __name__ == "__main__":
    main()