import paramiko

APIDIR = '/home/pi/Desktop/poaClient/PythonCode'
# Dateipfad zur api.py
NAME = 'pi'
PASS = 'testpw'

## master-Teil der kongruenten API - es gibt die entsprechenden Gegenfunktionen auf den sub-Pis
def connectSSH(ip):
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, NAME, PASS, banner_timeout = 2)
    except:
        return None
    return ssh  

def startGeth(ssh):
    apiAccess(ssh, 'startGeth()')
    
def startSession(ssh):
    apiAccess(ssh, 'startSession()')
    
def startUpdate(ssh):
    apiAccess(ssh,'startUpdate()')

def stopUpdate(ssh):
    apiAccess(ssh,'stopUpdate()')

def endSession(ssh):
    apiAccess(ssh,'endSession()')
                                        
def updatePro(ssh, pPWM):
    apiAccess(ssh,'updatePro('+str(pPWM)+')')
    
def updateCon(ssh, cPWM):
    apiAccess(ssh,'updateCon('+str(cPWM)+')')

def apiAccess(sshCon, command, close = False):
    stdin, stdout, stderr = sshCon.exec_command('cd '+APIDIR+'; python3 -c \'import api; api.'+command+'\'')
    if close:
        sshCon.close()
        
def apiAccessReturn(sshCon, command, close = False):
    stdin, stdout, stderr = sshCon.exec_command('cd '+APIDIR+'; python3 -c \'import api; api.'+command+'\'')
    returnString = (str(stdout.read(),'utf-8'))
    if close:
        sshCon.close()
    return returnString

def blankAccess(sshCon, command, close = False):
     stdin, stdout, stderr = sshCon.exec_command(command)
     if close:
        sshCon.close()
    
def blankAccessReturn(sshCon, command, close = False):
    stdin, stdout, stderr = sshCon.exec_command(command)
    returnString = (str(stdout.read(),'utf-8'))
    if close:
        sshCon.close()
    return returnString

    
def setContractAddress(ssh, newAddress):
    apiAccess(ssh,'setContractAddress('+str(newAddress)+')')

