import os
import configparser

FILEPATH = os.path.dirname(os.path.abspath(__file__))


cnfg = configparser.ConfigParser()
cnfg.read(FILEPATH+'/config.txt')
dtdir = FILEPATH+'/'+cnfg.get('Geth Launch','datadir')
ntwkid = cnfg.get('Geth Launch','networkid')
extip = cnfg.get('Geth Launch','extip')
port = cnfg.get('Geth Launch','port')
httpport = cnfg.get('Geth Launch','httpport')
acc = cnfg.get('Geth Launch','account')
pwf = FILEPATH+'/'+cnfg.get('Geth Launch','pwfile')
gasp = cnfg.get('Geth Launch','gasprice')
gaslim = cnfg.get('Geth Launch','gaslimit')
gascap = cnfg.get('Geth Launch','gascap')
txgcap = cnfg.get('Geth Launch','txgascap')
mintrds = cnfg.get('Geth Launch','minerthreads')
if cnfg.get('Geth Launch','mine') == 'true':
    pikeaxe = '--mine '
else:
    pikeaxe = ''              
os.system("geth --datadir "+dtdir+" --networkid "+ntwkid+" --nat extip:"+extip+" --unlock "+acc+" --password "+pwf+" --allow-insecure-unlock --rpc --rpcapi=\"db,eth,net,web3,personal,miner\" --miner.gasprice "+gasp+" --miner.gaslimit "+gaslim+" "+pikeaxe+"--miner.etherbase "+acc+" --miner.threads "+mintrds+" --port "+port+" --http.port "+httpport+" --rpc.gascap "+gascap+" --rpc.txfeecap "+txgcap+' --rpccorsdomain \"http://localhost:8000\"')
