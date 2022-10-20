# ME 106 Project Gesture and Temperature Controlled Fan
# Eulix Chiu, Michelle Ducard, Iqbal Singh
# 5-04-2021 Prof Furman

# Import Libraries
import time
import array
import math
import board
import audiobusio
from adafruit_apds9960.apds9960 import APDS9960
import adafruit_apds9960.apds9960
import adafruit_bmp280
import pwmio

# L298 Motor Board
ENA = pwmio.PWMOut(board.D12, duty_cycle = 0, frequency = 500)
IN1 = pwmio.PWMOut(board.D11, duty_cycle = 0, frequency = 500)
IN2 = pwmio.PWMOut(board.D10, duty_cycle = 0, frequency = 500)

# Microphone
i2c = board.I2C()
apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
apds = APDS9960(i2c)
apds9960.enable_proximity = True
apds9960.enable_color = True
apds.enable_proximity = True
apds.enable_gesture = True
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
microphone = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                              sample_rate=16000, bit_depth=16)
clap_threshold = 1000
rotate = True

def normalized_rms(values):                                       # Use normalised RMS average to take multiple sound samples really quickly and average them to get a more accurate reading.
    minbuf = int(sum(values) / len(values))
    return int(math.sqrt(sum(float(sample - minbuf) * (sample - minbuf) for sample in values) / len(values)))

def listen():
    samples = array.array('H', [0] * 160)
    microphone.record(samples, len(samples))
    sound = int(normalized_rms(samples))
    return sound

# DC Motor Rotation
def ENAmotor_level(level):
    ENA.duty_cycle = int(level/100*(65535-1))
def IN1motor_level(level):
    IN1.duty_cycle = int(level/100*(65535-1))
def IN2motor_level(level):
    IN2.duty_cycle = int(level/100*(65535-1))

# Setting up our PWM for fan
fan = pwmio.PWMOut(board.D13, duty_cycle = 0, frequency = 25000)
def fan_level(level):
    fan.duty_cycle = int(level/8 * (65535-1))

# 8 Levels for Fan Speed
levels = [[list(range(61))],[61,62,63,64],[65,66,67,68],[69,70,71,72],[73,74,75,76],[77,78,79,80],[81,82,83,84],[85,86,87,88],[89,90,91,92]]

dtc = 0
# Main Loop
while True:
    sound = listen()
    temperature = int((bmp280.temperature * 9/5) + 32) # converts celsius to fahrenheit
    gesture = apds.gesture()
    for i in range(len(levels)):
        for j in levels[i]:
            if j == temperature:
                dtc = i                         # the indice i represents the Fan Speed Level Based On temperature
                fan_level(dtc)
                print("Fan duty cycle is " + str(dtc))
                print(temperature)
                if gesture == 0x01:             # Fan Full Power            # must keep finger near gesture to activate
                    dtc = 8
                    fan_level(dtc)
                    print("up")
                    print("Fan duty cycle is at Max Power")
                elif gesture == 0x02:           # Fan Off
                    dtc = 0
                    fan_level(dtc)
                    print("down")
                    print("Fan duty cycle is off")
    if listen() > clap_threshold:               # if
        rotate = True
        while rotate == True:
            for i in range(0,70,10):                            # clockwise power up
                ENAmotor_level(i)
                IN1motor_level(i)
                time.sleep(.04)
                if listen() > clap_threshold:
                    rotate = False
                    break
            if rotate == False:
                break
            for i in range(70,-10,-10):                         # closewise power down
                IN1motor_level(i)
                time.sleep(.04)
                if listen() > clap_threshold:
                    rotate = False
                    break
            if rotate == False:
                break
            for i in range(0,60,10):                            # Counter clockwise power up
                IN2motor_level(i)
                time.sleep(.04)
                if listen() > clap_threshold:
                    rotate = False
                    break
            if rotate == False:
                break
            for i in range(60,-10,-10):                         # Counter clockwise power down
                IN2motor_level(i)
                time.sleep(.04)
                if listen() > clap_threshold:
                    rotate = False
                    break
            if rotate == False:
                break
        ENAmotor_level(0)                                       # After second clap, motor turns off
        IN1motor_level(0)
        IN2motor_level(0)
