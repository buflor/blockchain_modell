import csv

# Kleine Bibliothek zum erstellen, auslesen und bearbeiten von CSV-Dateien #
############################################################################


def newCSVFile(flNme, fldNms):
    try:
        with open('{}.csv'.format(flNme),'x',newline='') as csvfile:
            csv.DictWriter(csvfile, [y for y in fldNms]).writeheader()
    except FileExistsError:
        print('File already exists')
        pass
    
def getFieldNames(flNme):
    with open('{}.csv'.format(flNme),'r',newline='') as csvfile:
        return next(csv.reader(csvfile))

def addRow(flNme, content):           
    with open('{}.csv'.format(flNme),'a',newline='') as csvfile:
        csv.writer(csvfile).writerow(content)
                
def countRows(flNme):
    with open('{}.csv'.format(flNme),'r',newline='') as csvfile:
        return sum(1 for row in csv.reader(csvfile))

def openFileToArray(flname):
    with open('{}.csv'.format(flname),'r',newline='') as csvfile:
        reader = csv.reader(csvfile,delimiter = ';',quotechar='|')
        returnList = [row for row in reader]
        returnList.pop(0)
        return [int(str(x).strip('[\'\']')) for x in returnList]
 
