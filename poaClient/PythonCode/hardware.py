import lcddriver
import i2c_lib
import time
import board
import busio
import adafruit_ina219
import RPi.GPIO as GPIO
import random


# ADDRCONINA = 0x40
# ADDRPROINA = 0x41

# ADDRCONLCD = 0x27
# ADDRPROLCD = 0x26

RANDMIN = 0
RANDMAX = 10

# Meter-Klasse kombiniert die Kontrolle ueber ein INA219 und ein LCD-Display
class Meter:
    
    def __init__(self, mt, addrIna, addrLcd):
        self.exist = True
        try:
            self.mtype = mt
            self.ina = adafruit_ina219.INA219(busio.I2C(board.SCL, board.SDA), addrIna)
            self.dsp = lcddriver.lcd(addrLcd)
            self.dsp.lcd_display_string(self.mtype+" INA Pi-1",1)
            self.dsp.lcd_display_string("W: 0.0 - init",2)
        except:
            self.exist = False
        
    # Auslesen des INA-Messwerts, anzeigen auf dem Display, rueckgabe des Messwerts    
    def updateMeter(self, pwm = 0):
        if self.exist is True:
            wattage = self.ina.power
            bar = ''
            bar += 'I'*int(10*wattage/20)                
            self.dsp.lcd_display_string(self.mtype+": "+bar,1)
            self.dsp.lcd_display_string("W: {}".format(round(wattage,5)),2)
            return wattage
        else:
            return pwm #random.uniform(RANDMIN, RANDMAX)
    
    # ordentliches beenden (display leeren)
    def end(self):
        if self.exist:
            self.exist = False
            time.sleep(1)
            self.dsp.lcd_clear()
    
    # pause ohne beenden    
    def pause(self):
        if self.exist:
            self.dsp.lcd_clear()
            self.dsp.lcd_display_string("Con INA Pi-1",1)
            self.dsp.lcd_display_string("W: 0.0 - pausiert",2)
    
    # funktion zum leeren des Displays damit dies auch extern aufgerufen wereden kann
    def clearDsp(self):
        if self.exist:
            self.dsp.lcd_clear()
            
            
# Klasse mit welcher die motodriver2 Elemente gesteuert werden koennen
class Md2control:
    
    # einfache initialisierung mit den zugewiesenen Pins
    def __init__(self, in1, in2, pwm):
        
        # dutyC = dutyCycle = PWM wert zwischen 0 und 100
        self.dutyC = 0
        
        GPIO.setmode(GPIO.BCM)
        
        # Pin-einrichtung
        GPIO.setup(in1,GPIO.OUT)
        GPIO.setup(in2,GPIO.OUT)
        GPIO.setup(pwm,GPIO.OUT)
        
        # Outputrichtung festlegen
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        
        # aktivieren der PWM-Funktion
        self.pwmcontrol = GPIO.PWM(pwm, 1000)
        self.pwmcontrol.start(self.dutyC)
            
    # einstellen des DutyCycles, mit input-sanitizing
    def setPWM(self, target):
        if target < 0:
            target = 0
        if target > 100:
            target = 100
        
        # dutyCycle = 0-100% PWM
        self.pwmcontrol.ChangeDutyCycle(target)
        self.dutyC = target
        
            
    # aufraeumen der Pins        
    def end(self):
        self.dutyC = 0
        self.pwmcontrol.ChangeDutyCycle(self.dutyC)
        self.pwmcontrol.stop()
        
        # cleanup loescht pinzuweisung
        GPIO.cleanup()
        
        