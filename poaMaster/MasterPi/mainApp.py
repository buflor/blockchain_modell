import tkinter
import matplotlib.pyplot as mplpp
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as tkagg
import web3comm
import configparser
import threading
import os
import sys
import time
import random
import piclasso
import csv_caretaker
import math


APIDIR = '/home/pi/Desktop/poaClient/PythonCode'
PRNTPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = "800x480"
TIMERES = 15
MAXWINDABW = 0.15 #prozent

# Aufbau nach MVC-Modell.
# Die Controller Klasse stellt hier den C-Teil dar und verbindet die GUI mit der Blockchain und anderen Hintergrundaufgaben
class Controller():
    def __init__(self):
        
        # Objekt mit welchem die cfg-ausgelesen wird
        self.cfgPar = configparser.ConfigParser()
        self.cfgPar.read(PRNTPATH+'/config.txt')
        # Objekt dass die Kommunikation mit der Blockchain uebernimmt
        print(self.cfgPar.get('Web3','httpip'), self.cfgPar.get('Web3','httpport'), self.cfgPar.get('Contracts','con1'))
        self.w3c = web3comm.Web3Bridge(self.cfgPar.get('Web3','httpip'), self.cfgPar.get('Web3','httpport'), self.cfgPar.get('Contracts','con1'))
        
        
        # Die TK Klasse der Tkinter Bibliothek ist kernstueck der GUI.
        # Es ist das "Spielfeld" der GUI-Elemente
        self.root = tkinter.Tk()
        # festlegen der FEnsteraufloesung
        self.root.geometry(RES)
        # festtlegen des ersten Fensters
        self.viewer = StartFrame(self.root)
        
        self.piList = []
        
        for i, (name, ip) in enumerate(list(self.cfgPar.items('ips'))):
            self.piList.append(piclasso.PiClasso(name, ip, PRNTPATH+'/config.txt'))
            self.viewer.addLine(name, ip)
        self.viewer.progressBar()
        self.connectedPis = 0
        
        self.gethInit = False
        self.sessInit = False
        self.updaInit = False
        self.simInit = False
        
        # Einrichten der GUI-Elemente
        self.viewer.frame.pack()
        self.viewer.conSelBut.bind('<Button-1>', self.connectSel)
        self.viewer.conAllBut.bind('<Button-1>', self.connectAll)
        
        # Vorbereiten der regelmaessigen BC-Updates
        
        self.matchIntervall = tkinter.IntVar()
        self.matchIntervall.set(5)
        self.startBlock = self.w3c.getCurrentBlock()
    
    
    # Funktion die alle noetigen SSH-Verbindungen aufbaut und die tabs des Hauptframes vorbereitet
    # keine Fehlerbehandlung => unerreichbarer Pi => ProgStop!
    def buildingSSHConnections(self):       
        self.tabViewer = tkinter.ttk.Notebook(self.root)
        self.manualTab = ManualControlTab()
        tList = []
        pNum = -1
        for pi in self.piList:
            # auslagerung in Thread da gewartet werden muss bis geth vollständig gestartet ist
            # wenn angeschlossen werden ip und index im Thread genutzt um eine SSH Verbinudng auczubauen und eine Session zu starten
            if pi.active:
                if pi.pType != 'none':
                    pNum += 1
                    pi.pSlider = pNum
                pi.cSlider = self.connectedPis
                self.connectedPis += 1
                
                self.manualTab.addLine(pi.name, pi.cType, pi.pType)
                t = threading.Thread(target = self.connectThread, args =(pi,))
                tList.append(t)
        
        # Warteschleife waehrend Geth-Clients starten 
        for t in tList:
            self.viewer.pBar.step(int(20/self.connectedPis))
            self.root.update()
            t.start()
        if len(tList) > 0:
            self.viewer.pBar['value'] = 20
            self.root.update()
            for i in range(16*10):
                time.sleep(0.1)
                self.viewer.pBar.step(60/160)
                self.root.update()
            for t in tList:
                self.viewer.pBar.step(int(20/self.connectedPis))
                t.join()
                self.root.update()
            
        # stateVars dass geth und session gestartet wurden
        self.gethInit = True
        self.sessInit = True
        self.sessRun = False
        
        # tab wird hinzugefuegt
        self.tabViewer.add(self.manualTab.frame, text ='Kontrolle')
        self.w3c.setBatteryLoad(0)
        self.makeAndAddCharts()
        
        
    # Chart Tabs werden hinzugefuegt
    def makeAndAddCharts(self):
        self.chart1 = Chart1Tab()
        self.tabViewer.add(self.chart1.frame, text = 'Kreditaenderungen')
        self.chart2 = Chart1Tab()
        self.tabViewer.add(self.chart2.frame, text = 'Energiaenderungen')
        self.chart3 = Chart1Tab()
        self.tabViewer.add(self.chart3.frame, text = 'Energieverteilung')
        self.chart4 = Chart1Tab()
        self.tabViewer.add(self.chart4.frame, text = 'Preisentwicklung')
        self.chart5 = Chart1Tab()
        self.tabViewer.add(self.chart5.frame, text = 'Matched')
        self.bindAllTheButtons()
        

    # Funktion die allen Buttons ihnre Funktionen zuweist
    def bindAllTheButtons(self):
        self.manualTab.exitBut.bind('<Button-1>',self.endProgramm)
        self.manualTab.updateBut.bind('<Button-1>',self.updateVals)
        self.manualTab.stopBut.bind('<Button-1>',self.startStopUpdate)
        self.manualTab.updateSettingsButton.bind('<Button-1>', self.masterUpdate)
        self.manualTab.batButton.bind('<Button-1>', self.updateBatteryEff)
        self.chart1.updateFrameButton.bind('<Button-1>', self.updateChart1Plot)
        self.chart2.updateFrameButton.bind('<Button-1>', self.updateChart2Plot)
        self.chart3.updateFrameButton.bind('<Button-1>', self.updateChart3Plot)
        self.chart4.updateFrameButton.bind('<Button-1>', self.updateChart4Plot)
        self.chart5.updateFrameButton.bind('<Button-1>', self.updateChart5Plot)
        self.showMeWhatYouGot()
    
    # Anzeigen des endguelitgen Hauptfr1637237828.2705595ames
    def showMeWhatYouGot(self):
        self.viewer.frame.destroy()
        self.tabViewer.pack(expand = True, fill ='both')
     
      
    # jeder Pi wird in sienem eigenen Thread verbunden, welcher durch die SSH-Funktion aufgerufen wird
    def connectThread(self, pi):
        pi.connectDefaultSSH()
        time.sleep(1)
        if not self.viewer.internetBool.get():
            pi.syncTime()
        time.sleep(1)
        pi.startGeth()

        time.sleep(11)
        
        pi.startSession()
        time.sleep(2)
        
        
        
      
    
    # starten der mainloop, welche die GUI-Elemente kontrolliert
    def run(self):
        self.root.mainloop()
        
 ################# Button Functions:
    
    # Funktionen die durch die buttons der einzelnen Chart-Tabs aufgerufenen werden
    # hierdurch werden die angezeigten Graphen aktualsiert
    def updateChart1Plot(self, event):
        start = int(self.chart1.startEntry.get())
        end = int(self.chart1.endEntry.get())
        mplpp.close(self.chart1.activeFig)
        matchEvents = self.w3c.getMatchEvents(start, end)
        xData = []
        yDataList = []
        accounts = []
        print(matchEvents)
        for event in matchEvents:
            if event['args'].matched not in accounts:
                accounts.append(event['args'].matched)
                yDataList.append([])
            yDataList[accounts.index(event['args'].matched)].append(event['args'].creditChange)
            if event['blockNumber'] not in xData:
                for y in yDataList:
                    if len(xData) > len(y):
                        y.append(0)
                xData.append(event['blockNumber'])
        for y in yDataList:
            if len(xData) > len(y):
                y.append(0)
        print(len(xData))
        for y in yDataList:
            print (len(y))
        acc = [x[0:4] for x in accounts]
        self.chart1.plot.get_tk_widget().destroy()
        self.chart1.barChart2(xData, yDataList, acc, 'Block', 'Credit Change', 'Kreditaenderung Pro Block')
        self.chart1.plot = tkagg(self.chart1.activeFig, self.chart1.plotFrame)
        self.chart1.plot.get_tk_widget().pack(side='right', anchor='e', expand = True)


    def updateChart2Plot(self, event):
        start = int(self.chart2.startEntry.get())
        end = int(self.chart2.endEntry.get())
        mplpp.close(self.chart2.activeFig)
        enterEvents = self.w3c.getEnterEvents(start, end)
        xData = [x for x in range(start, end+1)]
        yData = []
        accounts = []
        print(enterEvents)
        for event in enterEvents:
            if event['args'].producer[0:4] not in accounts:
                accounts.append(event['args'].producer[0:4])
                yData.append(xData.copy())
            yData[accounts.index(event['args'].producer[0:4])][event['blockNumber']-start] = event['args'].offeredEnergy
        self.chart2.plot.get_tk_widget().destroy()
        self.chart2.barChart2(xData, yData, accounts,'Block','eingetragene Energie')
        self.chart2.plot = tkagg(self.chart2.activeFig, self.chart2.plotFrame)
        self.chart2.plot.get_tk_widget().pack(side='right', anchor='e', expand = True)
    
    
    def updateChart3Plot(self, event):
        start = int(self.chart3.startEntry.get())
        end = int(self.chart3.endEntry.get())
        mplpp.close(self.chart3.activeFig)
        genEvents = self.w3c.getGeneralInfo(start, end)
        legend = ['Batterieversorgung', 'Direktversorgung', 'Versorger', 'Batterieladung']
        print(genEvents)
        xData = []
        yData = [[],[],[],[]]
        for event in genEvents:
            yData[0].append(event['args'].batteryDelta)
            yData[1].append(event['args'].dCover)
            yData[2].append(event['args'].oDelta)
            yData[3].append(event['args'].bLoad)
            xData.append(event['blockNumber'])
        self.chart3.plot.get_tk_widget().destroy()

        self.chart3.linePlot(xData, yData, legend, 'Block', 'Ladung', 'Energieverteilung')
        self.chart3.plot = tkagg(self.chart3.activeFig, self.chart3.plotFrame)
        self.chart3.plot.get_tk_widget().pack(side='right', anchor='e', expand = True)
        
    def updateChart4Plot(self, event):
        start = int(self.chart4.startEntry.get())
        end = int(self.chart4.endEntry.get())
        mplpp.close(self.chart4.activeFig)
        genEvents = self.w3c.getGeneralInfo(start, end)
        legend = ['Direkt','Battery','V-Kauf', 'V-Verkauf']
        xData = []
        yData = [[],[],[],[]]
        for event in genEvents:
            yData[0].append(event['args'].dCoverPricePerUnit)
            yData[1].append(event['args'].bPricePerUnit)
            yData[2].append(event['args'].oBp)
            yData[3].append(event['args'].oSp)
            xData.append(event['blockNumber'])
        print(genEvents)
        self.chart4.plot.get_tk_widget().destroy()
        self.chart4.linePlot(xData, yData, legend, 'Block', 'Preis [Wei]', 'Preisentwicklung')
        self.chart4.plot = tkagg(self.chart4.activeFig, self.chart4.plotFrame)
        self.chart4.plot.get_tk_widget().pack(side='right', anchor='e', expand = True)
    
    def updateChart5Plot(self, event):
        start = int(self.chart5.startEntry.get())
        end = int(self.chart5.endEntry.get())
        mplpp.close(self.chart5.activeFig)
        matchEvents = self.w3c.getMatchEvents(start, end)
        xData = []
        yDataList = []
        accounts = []
        for event in matchEvents:
            if event['args'].matched not in accounts:
                accounts.append(event['args'].matched)
                yDataList.append([])
            yDataList[accounts.index(event['args'].matched)].append(event['args'].matchedEnergy)
            if event['blockNumber'] not in xData:
                for y in yDataList:
                    if len(xData) > len(y):
                        y.append(0)
                xData.append(event['blockNumber'])
        for y in yDataList:
            if len(xData) > len(y):
                y.append(0)
        print(len(xData))
        for y in yDataList:
            print (len(y))
        acc = [x[0:4] for x in accounts]
        self.chart5.plot.get_tk_widget().destroy()
        self.chart5.barChart2(xData, yDataList, acc, 'Block', 'Matched Energy', 'Gematchte Energie')
        self.chart5.plot = tkagg(self.chart5.activeFig, self.chart5.plotFrame)
        self.chart5.plot.get_tk_widget().pack(side='right', anchor='e', expand = True)
        
        
    # Verbinden der ausgewaehlten Pis
    def connectSel(self, event):
        #self.stateList = [x.get() for x in self.viewer.checkBools]
        for i, x in enumerate(self.viewer.checkBools):
            self.piList[i].active = x.get()
        self.buildingSSHConnections()
    
    # Verbinden aller Pis
    def connectAll(self, event):
        #andere sachen?
        self.buildingSSHConnections()
        
    # ordentliches beenden aller Komponenten
    def endProgramm(self, event = 0):
        if self.updaInit:
            self.startStopUpdate()
        for pi in self.piList:
            if pi.active:
                pi.gethSSH.close()
                pi.endSession()
                pi.defaultSSH.close()
        time.sleep(7)
        sys.exit()  

    
    # Funktion mit welcher alle Werte der konsumenten und produzenten aktualisiert werden    
    def updateVals(self, event):
        threadList = []
        for pi in self.piList:
            if pi.active:
                t = threading.Thread(target = self.updateThread, args=(pi,))
                threadList.append(t)
                t.start()
        for t in threadList:
            t.join(1)
         
     
    def startStopUpdate(self, event = 0):
        if not self.updaInit:
            if self.manualTab.simBoxVar.get() and (self.manualTab.jhzVar.get == 'Jahreszeit' or self.manualTab.tagVar.get() == 'Tag'):
                pass
            else:
                self.startUpdate()
        else:
            self.stopUpdate()
        self.manualTab.refreshSessionButtonText(self.updaInit)
        
    # starten und anhalten des Programms
 
    # aktualisieren der mastersettings aus der Gui heraus
    def masterUpdate(self, event):
        self.w3c.setBuyPrice(self.manualTab.buyPrice.get()*1000)
        self.w3c.setSellPrice(self.manualTab.sellPrice.get()*1000)
        self.matchIntervall.set(self.manualTab.matchSld.get())
    
    def updateBatteryEff(self,event):
        self.w3c.setBatteryEff(int(self.manualTab.batEffSlider.get()))
        self.w3c.setBatteryCapacity(int(self.manualTab.batCapSlider.get()))
############################ button sub functions
## Funktionen die durch die Buttons aufgerufen werden, aber nicht sinnvoll teil der Hauptfunktion sind
    
    def startUpdate(self):
        self.bgThread = threading.Thread(target = self.backgroundThread, args=())
        self.w3c.startMining()
        self.updaInit = True
        self.simThread = 0
        threadList = []
        for pi in self.piList:
            if pi.active:
                t = threading.Thread(target = pi.startUpdate, args =())
                threadList.append(t)
                t.start()
        for t in threadList:
            t.join(1)
        
        self.bgThread.start()
        if self.manualTab.simBoxVar.get():
            self.simInit = True
            self.simulationRunPrep()
            self.simThread.start()
    
    

    def stopUpdate(self):
        self.updaInit = False
        self.simInit = False
        self.bgThread.join(6)
        threadList = []
        for pi in self.piList:
            if pi.active:
                t = threading.Thread(target = pi.stopUpdate, args =())
                threadList.append(t)
                t.start()
        for t in threadList:
            t.join(1)
        self.w3c.stopMining()
        self.manualTab.resetSliders()
        


    def simulationRunPrep(self):
        start = self.manualTab.stzSlider.get()
        ende = self.manualTab.endSlider.get()
        windBase = self.manualTab.windBase.get()
        windVari = self.manualTab.windVari.get()
        
        inte = self.manualTab.intervall.get()
        reso = self.manualTab.resoloution.get()
        
        jhz = self.manualTab.jhzVar.get()[0:2]
        tag = self.manualTab.tagVar.get()[0:2]
        
        wohnDaten = csv_caretaker.openFileToArray(PRNTPATH+'/SimDaten/Wo'+tag+jhz)
        geweDaten = csv_caretaker.openFileToArray(PRNTPATH+'/SimDaten/Ge'+tag+jhz)
        sonnDaten = csv_caretaker.openFileToArray(PRNTPATH+'/SimDaten/So'+jhz)
    
        self.simThread = threading.Thread(target = self.simBackgroundThread, args=(start, ende, windBase, windVari, inte, reso, wohnDaten, geweDaten, sonnDaten))
        

    # Thread mit dem die einzelnen Pi-Werte aktualisiert werden
    def updateThread(self, pi):
        if not self.simInit:
            pi.updateCon(self.manualTab.sldsC[pi.sliderNumber].get()) 
            pi.updatePro(self.manualTab.sldsP[pi.sliderNumber].get()) 
        pi.updatePrice(self.manualTab.priceEntries[pi.sliderNumber].get())
        
############################ anything background thread
# Dieser thread laeuft immer wenn die aktualisierung der Pis gestartet wurde ununterbrochen
# aktuell enthalt dieser folgende Funktionen:
    # ausfuehren der matchfunktion in gegebenen Blockintervall
    # aktualisieren der Batterieladung in der GUI
    # bezahlen der Schulden des Hauptanbieters
    def backgroundThread(self):
        lastBlock = self.w3c.getCurrentBlock()
        self.bgStartBlock = lastBlock            
        while self.updaInit:

            
            self.matchIntervall.set(self.manualTab.matchSld.get())
            mi = self.matchIntervall.get()
            if mi != 0 and (self.w3c.getCurrentBlock()-self.bgStartBlock)%mi == 0:

                self.w3c.matchOrders()
                print("matching")
            while lastBlock == self.w3c.getCurrentBlock() and self.updaInit:
                time.sleep(0.2)
            lastBlock = self.w3c.getCurrentBlock()
            self.manualTab.batLoadVar.set(self.w3c.getBatteryLoad())
            self.w3c.coverCredit()
                
    def simBackgroundThread(self, start, ende, windBase, windVari, inte, reso, wohnDaten, geweDaten, sonnDaten):                
        simTimeInMins = start*60
        newWi = windBase
        startTime = time.time()
        tag = 1
        while (simTimeInMins < ende*60 or start == ende) and self.simInit:
            threadList = []
            targetTime = time.time()+inte
            currentIndex = math.floor(simTimeInMins/15)-(tag-1)*24*4
            print(currentIndex)
            newWo = int(sum(wohnDaten[currentIndex:currentIndex+reso])/reso)
            newGe = int(sum(geweDaten[currentIndex:currentIndex+reso])/reso)
            newSo = int(sum(sonnDaten[currentIndex:currentIndex+reso])/reso)

            newWi = int(newWi+newWi*random.uniform(-MAXWINDABW*reso, MAXWINDABW*reso))
            #if not max(0, windBase-windVari) <= newWi <= min(100, windBase+windVari):

            for pi in self.piList:
                if pi.active:

                    t = threading.Thread(target = self.simSubthread, args =(pi,newWo,newGe,newSo, newWi,))
                    threadList.append(t)
                    t.start()
            for t in threadList:
                t.join(1)
            while(time.time() < targetTime):
                simTimeInMins=math.floor((time.time()-startTime)/inte*15*reso)+start*60
                tag = math.floor(simTimeInMins/1440)+1
                self.manualTab.timeVar.set('Uhrzeit: Tag '+str(tag)+', '+str(math.floor(simTimeInMins/60-24*(tag-1))).zfill(2)+':'+str(simTimeInMins%60).zfill(2))

        self.manualTab.timeVar.set('Simulation Beendet')
        if self.simInit:
            self.stopUpdate()
            self.manualTab.refreshSessionButtonText(self.updaInit)
            
            
    def simSubthread(self, pi, wo, ge, so, wi):


        if pi.cType == 'Gewerbe':

            pi.updateCon(ge)
            self.manualTab.sldsC[pi.sliderNumber].set(ge)
            
        if pi.cType == 'Wohngebiet':

            pi.updateCon(wo)        
            self.manualTab.sldsC[pi.sliderNumber].set(wo)
            
        if pi.pType == 'Solar':

            pi.updatePro(so)
            self.manualTab.sldsP[pi.sliderNumber].set(so)
            
        if pi.pType == 'Wind':
 
            pi.updatePro(wi)
            self.manualTab.sldsP[pi.sliderNumber].set(wi)
            
############################################################
            # alles ab hier enthalt Klassen und Funktionen die die graphischen Elemente aufbauen und sortieren
            # recht redundant und "brute-forciges" Schema F:
                # 1) erstellen eines Frame Objekts in dem alle Elemente angeordnet werden
                # 2) erzeugen, hinzufuegen und sortieren aller darzustellenden Objekte (buttons, slider, ... usw)
                # 3) einzelne Listen und Variablen zum vereinfachten abrufen des Status eines Objekts
            # i.A. enthaelt der folgende Code keinerlei Logik - nicht mal einen Verweis auf diese

# im Startframe werden alle in der cfg hitnerlegten IP/name-Tupel mit checkbox angezeigt
# so kann ausgewaehlt werden welcher Pis verbunden werden sollen
class StartFrame():
    def __init__(self, parent):
        self.frame = tkinter.Frame(parent)
        self.slideFrame = tkinter.Frame(self.frame)
        self.butFrame = tkinter.Frame(self.frame)
        self.nameLabels = []
        self.checkBoxes = []
        self.checkBools = []
        
        self.conSelBut = tkinter.Button(self.butFrame, text = "Connect Selected")
        self.conSelBut.pack(side = 'right')
        
        self.conAllBut = tkinter.Button(self.butFrame, text = "Connect All")
        self.conAllBut.pack(side='right')
        
        self.internetBool = tkinter.BooleanVar()
        self.internetBox = tkinter.Checkbutton(self.butFrame, var = self.internetBool)
        self.internetlbl = tkinter.Label(self.butFrame, text = 'LAN-Kabel?')
        
        self.internetlbl.pack(side='left')
        self.internetBox.pack(side='left')
        
        
        self.butFrame.pack(side ='bottom')
        self.slideFrame.pack(side ='bottom')
        

    # hinzufuegen einer Zeile mit Name/IP/Checkbox
    def addLine(self, ip, name):      
        self.checkBools.append(tkinter.BooleanVar())       
        sf = tkinter.Frame(self.frame)
        lbl = tkinter.Label(sf, text=name+' @ '+ip)
        lbl.pack(side = 'left', anchor = 'nw')
        self.nameLabels.append(lbl)
        
        chkb = tkinter.Checkbutton(sf, var = self.checkBools[len(self.checkBools)-1])
        chkb.pack(anchor = 'ne')
        self.checkBoxes.append(chkb)
        sf.pack(anchor='n')
    # ein Fortschrittsbalken der waehrend des Verbindens angezeigt wird
    def progressBar(self):
        self.pBar = tkinter.ttk.Progressbar(self.frame, orient = 'horizontal', length = 100, maximum = 100, mode = 'determinate')
        self.pBar.pack(side ='top', fill ='both')
        self.frame.pack()
        print(self.pBar['value'])
        print(self.pBar['maximum']) 

    # funktion zum erhoehen der Variable im balken
    def incPVal(self, add):
        val = self.pBar['value']
        self.pBar['value'] = val+add
        print("val ",self.pBar['value'])

# Der MCT ist der Haupttab. hier werden alle Elemente generiert mit denen die Pis kontrolliert werden koennen
class ManualControlTab():
    def __init__(self):
        self.frame = tkinter.Frame()
        self.setAndBatFrame = tkinter.Frame(self.frame)
        self.rightFrame = tkinter.Frame(self.frame)

        self.manFrame = tkinter.Frame(self.rightFrame)
        self.simFrame = tkinter.Frame(self.rightFrame)
        self.butFrame = tkinter.Frame(self.rightFrame)
        
        #self.rightFrameSep = tkinter.ttk.Separator(self.rightFrame)
        #self.rightFrameSep.pack(side='bottom')
      
        self.exitBut = tkinter.Button(self.butFrame, text = "Beenden")
        self.exitBut.pack(side = 'right', expand = False)
        
        self.updateBut = tkinter.Button(self.butFrame, text = "Update Values")
        self.updateBut.pack(side ='right', expand = False)       
        
        self.stopBut = tkinter.Button(self.butFrame, text = "Start Update")
        self.stopBut.pack(side = 'right', expand = False)
        

        
        self.buyPrice = tkinter.Scale(self.setAndBatFrame, from_=1, to= 30, orient = 'horizontal', label = 'Buy Price x 1000', length =150)
        self.buyPrice.set(10)
        self.buyPrice.pack(anchor='w')
        
        self.sellPrice = tkinter.Scale(self.setAndBatFrame, from_=10, to=50, orient = 'horizontal', label = 'Sell Price x 1000', length = 150)
        self.sellPrice.set(30)
        self.sellPrice.pack(anchor='w')
        
        self.matchSld = tkinter.Scale(self.setAndBatFrame, from_=0, to=10, orient='horizontal', label ='Match Rate', length = 150)
        self.matchSld.set(5)
        self.matchSld.pack(anchor = 'w')
        
        self.updateSettingsButton = tkinter.Button(self.setAndBatFrame, text = 'Update Master', width = 14)
        self.updateSettingsButton.pack(anchor ='w')
        
        self.horizontSep = tkinter.ttk.Separator(self.setAndBatFrame, orient ='horizontal')
        self.horizontSep.pack(anchor='w', fill = 'both')
        
        self.batLoadVar = tkinter.IntVar()
        self.batCapVar = tkinter.IntVar()
        self.batCapVar.set(10000)
        self.batLoadVar.set(0)
        
        self.batLoadLbl = tkinter.Label(self.setAndBatFrame, text = 'Batterieladung:     '+str(self.batLoadVar.get()))
        self.batCapLbl = tkinter.Label(self.setAndBatFrame, text =  'Batteriekapazitaet: '+str(self.batCapVar.get()))
        self.batCapLbl.pack(anchor = 'sw')
        self.batLoadLbl.pack(anchor = 'sw')
        
        
        self.batBar = tkinter.ttk.Progressbar(self.setAndBatFrame, orient = 'horizontal', length = 150, maximum = self.batCapVar.get(), mode = 'determinate', variable = self.batLoadVar)
        self.batBar.pack(anchor = 'sw')
        self.batBar.after(4000, self.autoUpdateBattery)
        
        self.batEffSlider = tkinter.Scale(self.setAndBatFrame, orient = 'horizontal', from_ = 1, to = 100, label = 'Batterieeffizienz', length = 150)
        self.batEffSlider.set(90)
        self.batEffSlider.pack(anchor ='sw')
        
        self.batCapSlider = tkinter.Scale(self.setAndBatFrame, orient = 'horizontal', from_ = 0, to = 100000, resolution = 1000, label = 'Batteriekapazitaet', length = 150)
        self.batCapSlider.set(10000)
        self.batCapSlider.pack(anchor = 'sw')
        
        self.batButton = tkinter.Button(self.setAndBatFrame, text = 'Update Battery')
        self.batButton.pack(anchor ='sw')
        
        self.batInfoLbl = tkinter.Label(self.setAndBatFrame, text = 'Button leert Batterie!')
        self.batInfoLbl.pack(anchor ='sw')
        
        self.setAndBatFrame.pack(anchor='n', side = 'left', expand = False, fill ='none')
    
        self.verticalSep = tkinter.ttk.Separator(self.rightFrame, orient ='vertical')
        self.verticalSep.pack(side='left', fill = 'y')
        
        
        self.fillSimFrame()
        
        
        
        self.butFrame.pack(side='bottom', anchor='s',fill='x')
        self.manFrame.pack(side='right',anchor='n')
        
        self.simSep = tkinter.ttk.Separator(self.rightFrame, orient='vertical')
        self.simSep.pack(side='right',expand = True, anchor='n', fill='y')
        
        self.simFrame.pack(side='left',anchor ='n',expand = True, fill='both')
        self.rightFrame.pack(side='top', anchor ='w',fill='both', expand=True)
        
        self.sldsC = []
        #self.multC = []
        self.sldsP = []
        #self.multP = []
        self.priceEntries = []
        
        self.lblsL = []


    def fillSimFrame(self):
        
        self.sf1stRow = tkinter.Frame(self.simFrame)
        self.simLabel = tkinter.Label(self.sf1stRow, text='Enable Simulation')
        self.simLabel.pack(side='left',anchor='n')
        
        self.simBoxVar = tkinter.BooleanVar()
        self.simBox = tkinter.Checkbutton(self.sf1stRow, var = self.simBoxVar)
        self.simBox.pack(side='left', anchor='n')
        
        
        self.tagVar = tkinter.StringVar(value ='Tag')
        self.jhzVar = tkinter.StringVar(value ='Jahreszeit')
        
        self.tagOptionen = ['Werk','Sa' , 'So']
        self.jhzOptionen = ['Uebergang', 'Sommer', 'Winter']
        
        self.sf2ndRow = tkinter.Frame(self.simFrame)
        self.tagMenu = tkinter.OptionMenu(self.sf2ndRow, self.tagVar, *self.tagOptionen)
        self.tagMenu.pack(side='left',anchor='n')
        self.tagMenu.config(width=5)
        
        self.jhzMenu = tkinter.OptionMenu(self.sf2ndRow, self.jhzVar, *self.jhzOptionen)
        self.jhzMenu.config(width=12)
        self.jhzMenu.pack(side='left', anchor ='n')
        
        self.sf3rdRow = tkinter.Frame(self.simFrame)
        self.windBase = tkinter.Scale(self.sf3rdRow, from_=0, to=100, length=100, orient ='horizontal', label ='Wind Basis')
        self.windVari = tkinter.Scale(self.sf3rdRow, from_=0, to=100, length=100, orient='horizontal', label='Wind Varianz')
        self.windBase.pack(side = 'left', anchor='n')
        self.windVari.pack(side = 'left', anchor='n')
        
        self.sf4thRow = tkinter.Frame(self.simFrame)
        self.stzSlider = tkinter.Scale(self.sf4thRow, from_=0, to = 23, label = 'Startzeit', orient='horizontal')
        self.endSlider = tkinter.Scale(self.sf4thRow, from_=0, to = 24, label = 'Endzeit', orient = 'horizontal')
        self.endSlider.set(24)
        self.stzSlider.pack(side = 'left', anchor = 'n')
        self.endSlider.pack(side = 'left', anchor = 'n')
        
        self.sf5thRow = tkinter.Frame(self.simFrame)
        self.intervall = tkinter.Scale(self.sf5thRow, label = 'Intervall', from_= 1, to = 40, orient ='horizontal', length=125)
        self.resoloution = tkinter.Scale(self.sf5thRow, label = 'Res', from_= 1, to = 8, orient ='horizontal', length=75)
        
        self.intervall.set(4)
        self.resoloution.set(1)
        
        self.intervall.pack(side='left',anchor='n')
        self.resoloution.pack(side='left',anchor = 'n')
        
        self.sf6thRow = tkinter.Frame(self.simFrame)
        self.timeVar = tkinter.StringVar(value='Hello')
        self.timelabel = tkinter.Label(self.sf6thRow, textvariable=self.timeVar)
        self.timelabel.pack(side='left',anchor = 'n')
        self.timelabel.after(4000, self.autoUpdateTime)
        
        self.sf1stRow.pack(side='top')
        self.sf2ndRow.pack(side='top')
        self.sf3rdRow.pack(side='top')
        self.sf4thRow.pack(side='top')
        self.sf5thRow.pack(side='top')
        self.sf6thRow.pack(side='top')
        
        
        
# hinzufuegen einer Zeile mit Pi-spezifischen Elementen      
    def addLine(self, name, con, pro):
        f = tkinter.Frame(self.manFrame)
        lbl = tkinter.Label(f, text = 'name: '+name)
        self.lblsL.append(lbl)
        lbl.pack(side = 'left')
        
        if con != 'none':
            sCo = tkinter.Scale(f, from_=0, to=100, orient='horizontal', label = con, length=100)
            self.sldsC.append(sCo)
            sCo.pack(side ='left')
        if pro != 'none':
            sPo = tkinter.Scale(f, from_=0, to=100, orient='horizontal', label = pro, length=100)
            self.sldsP.append(sPo)
            sPo.pack(side = 'left')
            
            sPEntry = tkinter.Entry(f, width=6)
            sPEntry.insert(0, '20000',)

            sPEntry.pack(side = 'left')
            self.priceEntries.append(sPEntry)
            
        f.pack(anchor='n', expand = True)
        
    def refreshSessionButtonText(self, state):
        if state:
            self.stopBut.configure(text='Stop Update')
        else:
            self.stopBut.configure(text='Start Update')


    def resetSliders(self):
        for sC, sP in zip(self.sldsC, self.sldsP):
            sC.set(0)
            sP.set(0)

#funktion mit der der Batteristatus automatsich und stetig aktualisiert wird
    def autoUpdateBattery(self):
        self.batBar["value"] = self.batLoadVar.get()
        self.batLoadLbl['text'] = 'Batterieladung:       '+str(self.batLoadVar.get())
        self.batCapLbl['text'] =  'Batteriekapazitaet: '+str(self.batCapVar.get())
        self.batBar.after(200, self.autoUpdateBattery)
        
    def autoUpdateTime(self):
        self.timelabel['text'] = 'Uhrzeit: '+self.timeVar.get()
        self.timelabel.after(200, self.autoUpdateTime)
        
# alle weiteren Tabs sind Chart-Tabs. hier sind alle Funktionen definiert mit denen verschiedene Graphen angezeigt werden koennen    


class Chart1Tab():    
    def __init__(self):
        self.frame = tkinter.Frame()
        self.plotFrame = tkinter.Frame(self.frame)
        self.interactFrame = tkinter.Frame(self.frame)
        
        self.updateFrameButton = tkinter.Button(self.interactFrame, text='Update')
        self.updateFrameButton.pack(side='top',anchor='w')
        
        self.startEntry = tkinter.Entry(self.interactFrame,width = 8)
        self.startEntry.pack(side='top',anchor='w')
        
        self.endEntry = tkinter.Entry(self.interactFrame, width = 8)
        self.endEntry.pack(side='top', anchor='w')
        
        self.interactFrame.pack(side='left')
        self.activeFig = mplpp.figure()
        self.plot = tkagg(self.activeFig, self.plotFrame)
        self.plot.get_tk_widget().pack(side='right', anchor='e', expand = True, fill = 'both')
        
        self.plotFrame.pack(side='right', expand = True, fill = 'both')
        
        
    def linePlot(self, xData = [], yDataList = [], lgndList = [], xlbl = 'x', ylbl = 'y', titel = ''):
        mplpp.close(self.activeFig)
        self.activeFig = mplpp.figure()            
        for y in yDataList:
            mplpp.plot(xData, y, 'o--')

    
        mplpp.legend(lgndList)
        mplpp.ylabel(ylbl)
        mplpp.xlabel(xlbl)
        mplpp.title(titel)
        mplpp.grid()
      
    def barChart(self, xData = [], yData = [], lgnd = '', xlbl = 'x', ylbl = 'y'):
        mplpp.close(self.activeFig)
        self.activeFig = mplpp.figure()

        mplpp.bar(xData, yData)
        mplpp.legend(lgnd)
        mplpp.ylabel(ylbl)
        mplpp.xlabel(xlbl)
        mplpp.grid()

    def barChart2(self, xData = [], yDataList = [], lgndList = [], xlbl = 'x', ylbl = 'y', ttl = ''):
        mplpp.close(self.activeFig)
        self.activeFig, ax = mplpp.subplots()
        x = np.arange(len(xData))
        width = 0.3
        for i, y in enumerate(yDataList):
            ax.bar(((x + ((width*len(yDataList)/2)-width/2))-(width*i)), yDataList[i], width, label=lgndList[i])
        ax.set_ylabel(ylbl)
        ax.set_xlabel(xlbl)
        ax.set_title(ttl)
        ax.set_xticks(x)
        ax.set_xticklabels(xData)
        ax.legend()
        ax.grid()
        self.activeFig.tight_layout()
        
       

c = Controller()
c.run()
#model = Blockchain und Pis, view = windows controller = ?
 


