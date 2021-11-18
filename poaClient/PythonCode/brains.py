import signal
import os
import configparser
import time
import csv_caretaker
import sys

import hardware
import web3comm

import lcddriver
import i2c_lib

CFGFILE = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+'/cfg.txt'
PRNTPTH = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Hardcoden der I2C-Adressen und Pins für PWM-Kontrolle

# Consumer I2C Adressen
ADDRCONINA = 0x40
ADDRCONLCD = 0x27


# Producer I2C Adressen
ADDRPROINA = 0x41
ADDRPROLCD = 0x26

# Consumer Pins
CONPWM = 16 # => ENA
CONIN1 = 20 # => IN1
CONIN2 = 21 # => In2

# Producer Pins
PROPWM = 26  # => ENB
PROIN2 = 19  # => IN4
PROIN1 = 13 # => IN3
 
chainRate = 1 # pro block
updateRate = 0.2 # 1/F -> alle x sekunden

csvFelder = ['Time', 'pro', 'kon']

# Die Controller-Klasse steuert alle Hardwareelemente eines Client-Pis
class Controller:
    
    def __init__(self, cN = 1):
        #self.dbLcd = lcddriver.lcd(0x27)
        # self.debugLcd('display')
        
        # run: ob die Session initialisiert wurde
        # update: ob die Schleife zum updaten der Hardware laufen soll
        self.run = 1 
        self.update = 0
        self.cfg = configparser.ConfigParser()
        
        # wie PWM-Reset (Klassenfunktionen in __init__ nutzen??)
        self.setCfgVal('Kon','pwm',0)
        self.setCfgVal('Pro','pwm',0)
        
        # self.debugLcd('display', 'cfg')
        
        
        # OBjektinitialisierung der Web3-Kommunikatorklasse
        self.cfg.read(CFGFILE)
        hip = self.cfg.get('Web3', 'httpip')
        hpo = self.cfg.get('Web3', 'httpport')
        cAd = self.cfg.get('Contracts', 'con'+str(cN))
        self.bcTeller = web3comm.Web3Bridge(hip, hpo, cAd)
        self.activeContract = cN
        # self.debugLcd('bcT', 'cfg')
        
        # Auslesen ob Produzent/Konsument initialisiert werden soll
        self.prod = bool(self.getCfgVal('Pro','exist'))
        self.kons = bool(self.getCfgVal('Kon','exist'))
        self.pwmReset()
        print(self.kons)
        self.proPwm = 0
        self.conPwm = 0
        self.sellPrice = 20000
        
        # Initalisierung der Hardwarekontrollobjekte
        # Es werden nur die Initalisiert die laut CFG angeschlossen sind (s.o.)
        if self.kons:
            self.conMet = hardware.Meter("Con", ADDRCONINA, ADDRCONLCD)
            self.conMd2 = hardware.Md2control(CONIN1, CONIN2, CONPWM)
            self.cMulti = int(self.getCfgVal('Kon','multi'))
        if self.prod:
            self.proMet = hardware.Meter("Pro", ADDRPROINA, ADDRPROLCD)
            self.proMd2 = hardware.Md2control(PROIN1, PROIN2, PROPWM)
            self.pMulti = int(self.getCfgVal('Pro','multi'))
        
        
        self.sellRate = int(self.getCfgVal('General', 'sellrate'))
    
      
     
    # Liest das CFG-File neu ein und gibt einen ausgelesenen Wert zurueck      
    def getCfgVal(self, section, var):
        self.cfg.read(CFGFILE)
        return self.cfg.get(section, var)
    
    # Liest das CFG-File neu ein und schreibt einen gegebenen Wert neu
    def setCfgVal(self, section, var, value):
        self.cfg.read(CFGFILE)
        self.cfg.set(section, var,str(value))
        with open(CFGFILE,'w') as configfile:
            self.cfg.write(configfile)  
    
    # Setzt beide PWM-Vars im CFG-File auf 0 (und Preis
    def pwmReset(self):
        self.setCfgVal('Kon','pwm',0)
        self.setCfgVal('Pro','pwm',0)
        self.setCfgVal('General','sellprice',20000)
    # Liest die PWM-Vars im CFG-File aus.
    # wenn sich diese vom aktuellen Wert unterscheiden, wird der DutyCycle aktualisiert
    def updatePwm(self):
        if self.kons:
            self.conPwm = self.getCfgVal('Kon','pwm')
            if self.conPwm != self.conMd2.dutyC:
                self.conMd2.setPWM(int(self.conPwm))
                    
        if self.prod:
            self.proPwm = self.getCfgVal('Pro','pwm')  
            if self.proPwm != self.proMd2.dutyC:
                self.proMd2.setPWM(int(self.proPwm))
                
        # self.debugLcd('Pro: '+str(self.proPwm), 'Con: '+str(self.conPwm))
                
    # Liest beide INA219 aus und gibt Werte zurueck.
    # Ist kein INA219 angeschlossen wird 0 ausgegeben            
    def readout(self):
        return (time.time(), self.proMet.updateMeter(self.proPwm), self.conMet.updateMeter(self.conPwm))
    
    def pauseHardware(self):
        self.proMet.pause()
        self.conMet.pause()
        self.proMd2.setPWM(0)
        self.conMd2.setPWM(0)
    # bereitet das Log-File für die Session vor    
    def prepareLog(self):
        logNum = self.getCfgVal('General','log') # LogFiles werden stumpf durch nummeriert
        self.setCfgVal('General','log',int(logNum)+1) # entsprechend mir im CFG-File auch der LogFile-Zaehler erhoeht
        self.logName = PRNTPTH+'/logs/'+logNum
        
        csv_caretaker.newCSVFile(self.logName,csvFelder)
        csv_caretaker.addRow(self.logName,[self.bcTeller.getCurrentBlock(), self.bcTeller.getCurCadd(), self.bcTeller.getDefaultAddr()])
        
    # einfache LCD-Kontrolle fuer Debugging, irrelevant fuer normalen Betrieb
    def debugLcd(self, line1 = '', line2 = ''):
        self.dbLcd.lcd_clear()
        self.dbLcd.lcd_display_string(line1,1)
        self.dbLcd.lcd_display_string(line2,2)

    def updateSellPrice(self):
        self.sellPrice = self.getCfgVal('General', 'sellprice')
    
    # Endlossschleife die die PWM-Werte aktualisiert und INA219-Messwerte konstant und regelmaessig ausliest
    def updateLoop(self):
        self.prepareLog()
 
        
        delta = 0
        messpunkte = 0 
        while self.run == 1:
            if self.update == 1:
                self.conMet.clearDsp()
                self.proMet.clearDsp()
                lastSellBlock = 0
                sellTime = time.time()            
                while self.update == 1:
                    self.updatePwm()
                    print("upd")
                    crt, proWatt, konWatt = self.readout()
                    messpunkte += 1
                    delta += int(proWatt)*self.pMulti-int(konWatt)*self.cMulti
                    self.updateSellPrice()
                    if self.bcTeller.getCurrentBlock() >= lastSellBlock+chainRate:
                        lastSellBlock = self.bcTeller.getCurrentBlock()
                        # mitteln der messwerte
                        if messpunkte is not 0:
                            delta = int(delta/messpunkte*(time.time()-sellTime))
                        if delta > 0:
                            print('sell')
                            self.bcTeller.coverCredit() 
                            self.bcTeller.enterEnergy(int(delta), int(self.sellPrice))
                        if delta < 0:
                            self.bcTeller.enterEnergy(int(delta), int(self.sellPrice))
                            print('buy')
                            self.bcTeller.coverCredit() 
                    
                    # zuruecksetzen der Werte       
                        sellTime = time.time()
                        messpunkte = 0
                        delta = 0
                        
                    # Einfuegen der Messwerte in die Log-Datei
                    csv_caretaker.addRow(self.logName,[crt, konWatt, proWatt])
                    try:
                        time.sleep(crt+updateRate-time.time())
                    except:
                        pass
                    # auslesen der update var. wenn udpate == 0, wird die Schleife beendet
                    self.update = int((self.getCfgVal('General','update')))
                    if self.update == 0:
                        messpunkte = 0
                        delta = 0
                        self.pauseHardware()
                    
            # Auslesen der update und run variable, ob das Programm in die Schleife gehen soll oder warten oder beenden
            self.update = int((self.getCfgVal('General','update')))
            self.run = int(self.getCfgVal('General','run'))
            
            
        # self.debugLcd('exiting')
        
        # ordentliches beenden der Hardwarekontrolle zur Fehlervermeidung
        # (note: geth wird durch schließen der SSH-Verbindung auf dem Haupt-Pi beendet)
        self.conMet.end()
        self.proMet.end()
        self.conMd2.end()
        self.proMd2.end()
        self.pwmReset()
        
        # self.dbLcd.clear()
        
        sys.exit() 
 
 
 
   


