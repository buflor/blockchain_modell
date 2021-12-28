import lcddriver
import i2c_lib
import time
import board
import busio
import adafruit_ina219
import RPi.GPIO as GPIO


def testEmAll():
    
    # Consumer  INA test - Adresse 0x40
    inaTest(0x40)
    # Producer  INA test - Adresse 0x41 - gelötet
    inaTest(0x41)
    
    # Consumer  LCD test - Adresse 0x27
    lcdTest(0x27)
    # Producer  LCD test - Adresse 0x26 - gelötet
    lcdTest(0x26)
    
    # Consumer  MD2 test 
    md2Test(20, 21, 16)
    # produrcer MD2 test
    md2Test(13, 19, 26)
    print("done")
        
    
def inaTest(addr):
    try:
        ina = adafruit_ina219.INA219(busio.I2C(board.SCL, board.SDA), addr)
        time.sleep(1)
        print("INA "+str(addr)+" funktioniert. "+str(ina.power)+" Watt!")
    except:
        print("INA "+str(addr)+" failed.")
        
    
def lcdTest(addr):
    try:
        dsp = lcddriver.lcd(addr)
        time.sleep(1)
        dsp.lcd_display_string("TestTest123",1)
        dsp.lcd_display_string("Zeile 2",2)
    except:
        print("LCD "+str(addr)+" failed.")
    
def md2Test(in1, in2, pwm):
        GPIO.setmode(GPIO.BCM)
        # Pin-einrichtung
        GPIO.setup(in1,GPIO.OUT)
        GPIO.setup(in2,GPIO.OUT)
        GPIO.setup(pwm,GPIO.OUT)     
        # Outputrichtung festlegen
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        # aktivieren der PWM-Funktion
        pwmcontrol = GPIO.PWM(pwm, 1000)
        pwmcontrol.start(50)
        time.sleep(2)
        pwmcontrol.ChangeDutyCycle(10)
        time.sleep(2)
        pwmcontrol.ChangeDutyCycle(100)
        time.sleep(2)
        pwmcontrol.ChangeDutyCycle(0)
        time.sleep(2)
        pwmcontrol.ChangeDutyCycle(75)
        

    