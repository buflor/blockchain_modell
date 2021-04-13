import configparser
import paramiko
import time
import os

SSHNAME = 'pi'
SSHPASS = 'testpw'
SSHAPIDIR = '/home/pi/Desktop/poaClient/PythonCode'
PRNTPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class PiClasso:
    def __init__(self, name_, ip_, cfg_):
        self.ip = ip_
        self.name = name_
        self.active = True
        self.cfgPath = cfg_
        self.cfgPar = configparser.ConfigParser()
        self.cfgPar.read(self.cfgPath)
        
        (garb1, self.cType), (garb2, self.pType) = self.cfgPar.items(self.name)

        self.gethSSH = 0
        self.sessSSH = 0
        self.defaultSSH = 0
        
        self.cVal = 0
        self.pVal = 0
        
        self.pSlider = -1
        self.cSlider = -1

        self.currentPrice = 20000
        
    
    def connectDefaultSSH(self):
        self.defaultSSH = self.connectSSH()
        
        
    def startGeth(self):
        if self.gethSSH is 0:
            self.gethSSH = self.connectSSH()
            self.apiAccess(self.gethSSH, 'startGeth()')

            
    
    def startSession(self):
        if self.sessSSH is 0:
            self.sessSSH = self.connectSSH()
            self.apiAccess(self.sessSSH, 'startSession()')
            
            
    def endSession(self):
        self.apiAccess(self.defaultSSH,'endSession()')
    
    
    def startUpdate(self):
        self.apiAccess(self.defaultSSH,'startUpdate()')


    def stopUpdate(self):
        self.apiAccess(self.defaultSSH,'stopUpdate()')

                                            
    def updatePro(self, pPWM):
        print(self.pVal, pPWM)
        if pPWM is not self.pVal:
            self.apiAccess(self.defaultSSH,'updatePro('+str(pPWM)+')')
            self.pVal = pPWM
            print("pval upd")
            
    def updateCon(self, cPWM):
        print(self.cVal, cPWM)
        if cPWM is not self.cVal:
            self.apiAccess(self.defaultSSH,'updateCon('+str(cPWM)+')')
            self.cVal = cPWM
            print("cval upd")
            
    def updatePrice(self, newPrice):
        if newPrice is not self.currentPrice:
            try:
                newPrice = int(newPrice)
                self.apiAccess(self.defaultSSH, 'updatePrice('+str(newPrice)+')')
                self.currentPrice = newPrice
            except:
                pass
      
    def syncTime(self):
        self.apiAccess(self.defaultSSH, 'setTime('+str(time.time())+')')
        
            
        
        
    def connectSSH(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, 22, SSHNAME, SSHPASS, banner_timeout = 2)
        except:
            return None
        return ssh 
    
    def apiAccess(self, sshCon, command):
        stdin, stdout, stderr = sshCon.exec_command('cd '+SSHAPIDIR+'; python3 -c \'import api; api.'+command+'\'')
