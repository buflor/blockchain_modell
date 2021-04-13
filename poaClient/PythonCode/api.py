import os
import configparser
import time
import sys
#import noHardware
import brains

FILEPATH = os.path.dirname(os.path.abspath(__file__))
PRNTPATH = os.path.dirname(FILEPATH)
CFGFILE = PRNTPATH+'/cfg.txt'

def shutdown(delay, modifier = 'h'):
    time.sleep(delay)
    os.system('sudo shutdown -'+modifier+' now')

def setTime(unixtimestamp):
    os.system('sudo date -s @\''+str(unixtimestamp)+'\'')

def getCfgVal(section, var):
    cfg = configparser.ConfigParser()
    cfg.read(CFGFILE)
    print(cfg.get(section,var))

def setCfgVal(section, var, value):
    cfg = configparser.ConfigParser()
    cfg.read(CFGFILE)
    cfg.set(section, var,str(value))
    with open(CFGFILE,'w') as configfile:
        cfg.write(configfile)    

# funktionen die signale an die spezifizierte prozessid schicken - aktuell nicht verwendet
def sendSig1To(pidRec):
    os.system('sudo kill -s SIGUSR1 {}'.format(int(pidRec)))
    
def sendSig2To(pidRec):
    os.system('sudo kill -s SIGUSR2 {}'.format(int(pidRec)))

   
def endNoHardware():  
    cfg = configparser.ConfigParser()
    cfg.read(CFGFILE)
    sendSig1To(cfg.get('pids','noHardware'))

def startGeth():
    
    cnfg = configparser.ConfigParser()
    cnfg.read(CFGFILE)
    
    # --datadir = Ordner des Ethereum-Knotens
    dtdir = PRNTPATH+'/'+cnfg.get('Geth Launch','datadir')
    
    # blockchain-id
    ntwkid = cnfg.get('Geth Launch','networkid')
    
    # eigene Ip adresse
    extip = cnfg.get('Geth Launch','extip')
    
    # port fuer BC-kommunikation
    port = cnfg.get('Geth Launch','port')
    
    # port fuer zugriff durch python
    httpport = cnfg.get('Geth Launch','httpport')
    
    # account adresse
    acc = cnfg.get('Geth Launch','account')
    
    # passwort-datei
    pwf = PRNTPATH+'/'+cnfg.get('Geth Launch','pwfile')
    
    # gaspreis
    gasp = cnfg.get('Geth Launch','gasprice')
    
    # Gaslimit eines Aufrufs
    gaslim = cnfg.get('Geth Launch','gaslimit')
    
    # Anzahl Threads die zum minen gneutzt werden
    mintrds = cnfg.get('Geth Launch','minerthreads')
    
    # gascap - unterschied zu gaslimit? (definitiv anders, aber wie genau?)
    gascap = cnfg.get('Geth Launch','gascap')
    
    # transactionfeecap - wie gascap nur fuer transaktion
    txfeecap = cnfg.get('Geth Launch','txfeecap')
    if cnfg.get('Geth Launch','mine') == 'true':
        pikeaxe = '--mine '
    else:
        pikeaxe = ''              
    os.system("geth --datadir "+dtdir+" --networkid "+ntwkid+" --nat extip:"+extip+" --unlock "+acc+" --password "+pwf+" --allow-insecure-unlock --rpc --rpcapi=\"db,eth,net,web3,personal,miner\" --miner.gasprice "+gasp+" --miner.gaslimit "+gaslim+" "+pikeaxe+"--miner.etherbase "+acc+" --miner.threads "+mintrds+" --port "+port+" --http.port "+httpport+ ' --rpc.gascap '+gascap+' --rpc.txfeecap '+txfeecap)

def endGeth():
    x = os.popen('sudo pgrep -x geth').read()
    os.system('sudo kill -9 '+x)
    
# beim session start werden zur sicherheit alle werte erneut zurueckgesetzt
# so wird ein fruehstart vermieden
def startSession():
    setCfgVal('General','run','1')
    stopUpdate()
    updatePro(0)
    updateCon(0)
    puppetMaster = brains.Controller()
    puppetMaster.updateLoop()
    
def startUpdate():
    setCfgVal('General','update','1')
    
def stopUpdate():
    setCfgVal('General','update','0')
    
def endSession():
    stopUpdate()
    setCfgVal('General','run','0')
    
def updatePro(pPWM):
    str(int(pPWM))
    setCfgVal('Pro','pwm',pPWM)
    
def updateCon(cPWM):
    str(int(cPWM))
    setCfgVal('Kon','pwm',cPWM)
    
def setContractAddress(newAddress):
    setCfgVal('Contracts','con1',str(newAdress))
    
def updatePrice(price):
    setCfgVal('General','sellprice',str(price))

