# WeatherPico2W – Pico W IoT Weather Station

_Want to know the temperature in Sasolburg, or just need an excuse to justify your purchase of yet another Raspberry Pi Pico W? Either way, welcome!_

WeatherPico2W is a minimalist weather station for your Pi Pico W, using a BME280 sensor, a rain sensor, and a highly developed sense of existential dread every time WiFi drops. Telemetry is beamed to InfluxDB for slick dashboarding and even slicker graphs.

## Features
- Connects to WiFi, or dies trying (and reboots for good measure).
- Syncs time the only way a microcontroller should—by pestering NTP until it works.
- Reads temperature, pressure, and humidity via BME280; rain via ADC.
- Posts weather data to InfluxDB with all the enthusiasm of a British summer.
- LED status indication for everything: Success, failure, existential crisis.
- Optimistically attempts to fix everything by rebooting.

## Hardware Required
- Raspberry Pi Pico W
- BME280 sensor (I2C)
- Rain sensor (Analog)
- A sense of humour when things go sideways

## Configuration

Edit these in the script before deployment (or—brace yourself—use environment variables):

```python
SSID = ""
PASSWORD = ""
INFLUXDB_URL = "http://ip:8086/api/v2/write?org=&bucket=&precision=s"
INFLUXDB_TOKEN = "<your_super_secret_token>"
SDA_PIN = 16
SCL_PIN = 17
RAIN_SENSOR_PIN = 26
```
_Want more security? Don’t publish your credentials on GitHub._

## Running

1. Add `bme280_float.py`, Dependency libraries, and your script to the Pico W.
2. Power up. Beam the data!
3. Watch your InfluxDB for incoming weather stats.
4. For anything else, pray to the microcontroller gods, or check the LED patterns.

## What’s with the LEDs?

- **3 quick blinks:** WiFi connected (hooray!)
- **5 quick blinks:** WiFi failure (boo!)
- **1 slow blink:** Data sent to InfluxDB (fist bump)
- **4 quick blinks:** Data sending failed, panic!
- **6 dramatic blinks:** General fatal error, reset incoming!

## Troubleshooting

- Keeps rebooting? Double-check your WiFi or InfluxDB credentials.
- Sensor data is “None” or nonsensical? Wires probably in the wrong holes.
- Still stuck? Ask your neighbour. Or raise an issue.

## License

MIT. Blame yourself for what happens next.

---

## Tags

**Broad Categories**
- Technology
- Electronics
- Open Source

**Specific Subtopics**
- IoT Projects
- Weather Monitoring
