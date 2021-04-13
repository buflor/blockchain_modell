import web3
import time
import contractAbis
import eth_account

# Klasse ueber welche die Kommunikation mit der Blockchain stattfindet.
# basiert stark auf der web3py-Bibliothek
class Web3Bridge: 
    def __init__(self, httpip, httpport, cAddr, addrNum = 0):
        self.conAddr = '0x'+cAddr
        self.conAbi = contractAbis.abi
        
        # web3 Objekt aus der web3py Klasse, mit middleware injection damit die PoA-Chain genutzt werden kann
        self.w3 = web3.Web3(web3.HTTPProvider('http://'+httpip+':'+httpport))            
        self.w3.middleware_onion.inject(web3.middleware.geth_poa_middleware, layer=0)        
        
        self.exchange = self.w3.eth.contract(address=self.conAddr, abi=self.conAbi)
        self.w3.eth.defaultAccount = self.w3.geth.personal.list_accounts()[addrNum]
    
    ## definition der Contract-Funktionen die aufgerufen werden
    def matchOrders(self):
        self.exchange.functions.matchOrders().transact()
    
    def enterEnergy(self, energy, price):
        print("Entering: ", energy, price)
        self.exchange.functions.enterEnergy(int(energy), price).transact()
    
    def coverCredit(self):
        credit = self.getOwnCredit()
        print("Cred: ", credit)
        if credit < 0:
            print("paying: ", -1*credit)
            self.exchange.functions.coverCredit().transact({'value': -1*credit})
    
    def getBatteryLoad(self):
        try:
            return self.exchange.functions.getBatteryLoad().call()
        except:
            return 0
    
    def setBatteryLoad(self, newLoad):
        self.exchange.functions.setBatteryLoad(newLoad).transact()
    
    def setBatteryCapacity(self, newCap):
        self.exchange.functions.setBatteryCapacity(newCap).transact()
    
    def setBatteryEfF(self, newEff):
        self.exchange.functions.setBatteryEff(newEff).transact()
        
    def setBuyPrice(self, newPrice):
        self.exchange.functions.setBuyPrice(int(newPrice)).transact()
        
    def setSellPrice(self, newPrice):
        self.exchange.functions.setSellPrice(int(newPrice)).transact()
        
    def getOwnCredit(self):
        try:
            return self.exchange.functions.getCredit().call()
        except:
            return 0
    
    def getAccountCredit(self, address):
        try:
            return self.exchange.functions.getSpecCredit(address).call()
        except:
            return 0
    

    # einige getter Funktionen  
    def getCurrentBlock(self):
        return self.w3.eth.getBlock('latest')['number']
    
    def getCurCadd(self):
        return self.conAddr
    
    def getDefaultAddr(self):
        return self.w3.eth.defaultAccount
    
    def getEnterEvents(self, start=0, end ="latest"):
        if start < 0:
            start = 0
        if end > self.getCurrentBlock():
            end = 'latest'
        if start > end:
            helpVar = end
            end = start
            start = helpVar
            
        return self.exchange.events.enterEvent().createFilter(fromBlock = start, toBlock = end, address=self.conAddr).get_all_entries()

    def getMatchEvents(self, start=0, end ="latest"):
        if start < 0:
            start = 0
        if end > self.getCurrentBlock():
            end = 'latest'
        if start > end:
            helpVar = end
            end = start
            start = helpVar
            
        return self.exchange.events.matchEvent().createFilter(fromBlock = start, toBlock = end, address=self.conAddr).get_all_entries()
    
    def getGeneralInfo(self, start=0, end ="latest"):
        if start < 0:
            start = 0
        if end > self.getCurrentBlock():
            end = 'latest'
        if start > end:
            helpVar = end
            end = start
            start = helpVar
            
        return self.exchange.events.generalInfo().createFilter(fromBlock = start, toBlock = end, address=self.conAddr).get_all_entries()
    
    def startMining(self):
        self.w3.geth.miner.start(1)
        
    def stopMining(self):
        self.w3.geth.miner.stop()




    

     

        

