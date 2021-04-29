pragma solidity ^0.5.0;


contract proportionalBattery {
    event enterEvent(address indexed producer, int offeredEnergy, int sellPrice);
    event matchEvent(address indexed matched, int matchedEnergy, int creditChange);
    event generalInfo(int dCover, int dCoverPricePerUnit, int batteryDelta, int bLoad, int bPricePerUnit, int oDelta, int oBp, int oSp);
    event contractPay(address indexed partner, int amountPayed, int credit);
    
    address payable owner;
    
    int batteryCapacity = 10000;
    int batteryLoad = 0;
    int totalBatteryPrice = 0;
    int8 batteryEfficiency = 90;
    
    int ownerBuyPrice = 10000; // Preis fuer den der Owner Energie aus der BC kauft
    int ownerSellPrice = 30000; // Preis fuer den der Owner Energie in die BC verkauft
    int ownerCredit = 0;
    
    
    struct bookKeepersPage {
        int256 energy;
        int256 credit;
        int256 sellPrice;
        uint8 updateBlock;
        uint256 matchBlock;
        uint256 deletionBlock;
        int256 matchedEnergy;
        
    }
    
    address payable[] members;
    mapping(address => bookKeepersPage) bookKeep;

    constructor (int bp, int sp) public {
        ownerBuyPrice = bp; 
        ownerSellPrice = sp; 
        owner = msg.sender;

    }
    
    
    // Der Bedarf einer Matching-Funktion ergibt sich aus dem Problem des Double-Spendings
    // Dieses ist in Ethereum drakonisch geloest, indem bei Konflikten nur die zuerst eingegangene Transaktion beruecksichtigt wird
    // Damit ein automatisierter Handel stattfinden kann (ohne Benachteiligung aus technischen Gruenden oder anderen Ausgleichsmechanismen)
    // werden Kauf- und Verkaufs-Gesuche aufgegeben die dann zentral in regelmaessigen Abstanden miteinander ab- und ausgeglichen werden
    // Dieser Ansatz ist grundsaetzlich nicht im Sinne der Blockchaingrundlagen, ist jedoch fuer diesen anwendungsfall notwendig
    
    function matchOrders() external {
        // nur der owner kann diese Funktion ausloesen
        require (msg.sender == owner);
        
        // vars fuer summen produzierter und konsumierter Energie 
        int sumPro = 0;
        int sumCon = 0;
        int priceSum = 0;
        
        // Schleife die die "Konten" aller Mitglieder einmal durchgeht
        for (uint i = 0; i < members.length; i++){
            if (address(this).balance != 0 && bookKeep[members[i]].credit > 0){
                if (bookKeep[members[i]].credit > int(address(this).balance)) {
                    emit contractPay(members[i], int(address(this).balance)*-1, bookKeep[members[i]].credit-int(address(this).balance));
                    bookKeep[members[i]].credit -= int(address(this).balance);
                    address(members[i]).transfer(address(this).balance);
                }
            
            
            // falls der Vertrag die Schulden komplett ausgleichen kann
                else {
                    emit contractPay(members[i], bookKeep[msg.sender].credit*-1, 0);
                    address(members[i]).transfer(uint(bookKeep[msg.sender].credit));
                    bookKeep[members[i]].credit = 0; 
                }
            }
            // falls es seit dem letzten match zu Updates gekommen ist wird die neue Energie
            // fuer die summen beruecksichtigt
            // Energiemenge Pos => aufaddiert auf sumPro
            // Energiemenge Neg => abgezogen(!) von sumCon 
            // => sumpro und sumcon sind beide positiv!
            if (bookKeep[members[i]].matchBlock < bookKeep[members[i]].deletionBlock) {
                bookKeep[members[i]].matchedEnergy = 0;
                if(bookKeep[members[i]].energy < 0) {
                    sumCon -= bookKeep[members[i]].energy;
                }
                else {
                    sumPro += bookKeep[members[i]].energy;
                    priceSum += bookKeep[members[i]].sellPrice*bookKeep[members[i]].energy;
                }
            }
            
        }
        // BAD PRACTICE!
        if (address(this).balance != 0 && ownerCredit > 0){
            if (ownerCredit > int(address(this).balance)){
                emit contractPay(owner, int(address(this).balance)*-1, ownerCredit - int(address(this).balance));
                ownerCredit -= int(address(this).balance);
                msg.sender.transfer(address(this).balance);
            }
            else{
                emit contractPay(owner, ownerCredit*-1, 0);
                msg.sender.transfer(uint(ownerCredit));
                ownerCredit = 0;
            }
        }
        int directCoverPricePerUnit = 0;
        if (sumPro > 0){
            directCoverPricePerUnit = priceSum/sumPro;
        }
        // weitere Hilfsvariablen
        
        
        // freie Batterienkapazitaet
        int freeCapacity = batteryCapacity-batteryLoad;
        
        // Energiedifferenz
        int delta = sumPro-sumCon;
        
        // Energieueberschuss an Owner
        int toOwner = 0;
        
        // Energie die in Batterie geht
        int toBattery = 0;
        
        // erzeugte Energie die direkt an Verbraucher geht
        int directCover = 0;
        
        // energie des owners die zum ausgleich benoetigt wird
        int fromOwner = 0;
        
        // energie die aus der Batterie gezogen wird
        int fromBattery = 0;
        
        int batteryPricePerUnit = 0;
        // falls mehr/gleich produziert als(wie verbraucht wurde
        if (delta > 0){
            
            // konsumierte Energie wird zu 100% direkt bedient
            directCover = sumCon; 
            
            // falls die Batterie den Ueberschuss nicht aufnehmen kann
            if (freeCapacity < delta) {
                toBattery = freeCapacity;
                toOwner = delta-freeCapacity;
            }
            // falls die Batterie alles aufnehmen kann
            else {
                toBattery = delta;
            }
            
            // technisch gesehen ist dies nichts weiter als eine manuelle min-Funktion (min(freeCapacity, delta))
            // denn in jedem Fall erhoeht sich die Batterieladung um den minimalen Wert
            // aus freier Kapazitaet und Delta
            if (toBattery > 0){
                totalBatteryPrice += directCoverPricePerUnit*toBattery;
            }
            batteryLoad += toBattery*batteryEfficiency/100;
        }
        
        // falls mehr verbraucht wurde:
        else {
            
            // jede erzeugte Energie wird genutzt um direkt den Verbrauch zu stillen
            // auch hier ist directCover = min(sumPro,sumCon)
            directCover = sumPro;
            
            // falls die Batterladung nicht ausreicht um den Ueberschuss zu stillen
            if (batteryLoad < delta*-1) {
                
                // ist die Energie aus der Batterie gleich der Ladung 
                fromBattery = batteryLoad;
                
                // fehlende Energie wird vom Owner nachgekauft
                fromOwner = (delta*-1)-batteryLoad;
            }
            // ist genug da...
            else {
                
                // ...ist der Ueberschuss gleich der benoetigten Menge aus der Batterie
                fromBattery = delta*-1;
            }
            if (fromBattery > 0){
                batteryPricePerUnit = totalBatteryPrice/batteryLoad;
                totalBatteryPrice -= batteryPricePerUnit*fromBattery;
            }
            // und die Batterieladung reduziert sich um den entsprechenden betrag (fromBattery = min(delta*-1, batteryLoad))
            batteryLoad -= fromBattery;
            if (batteryLoad == 0){
                totalBatteryPrice = 0;
            }
        }
        if (batteryPricePerUnit >= ownerSellPrice && fromBattery != 0){
            batteryPricePerUnit = ownerSellPrice-1;
            totalBatteryPrice = batteryPricePerUnit*batteryLoad;
        }
        if (batteryPricePerUnit <= directCoverPricePerUnit && fromBattery != 0){
            batteryPricePerUnit = directCoverPricePerUnit+1;
            totalBatteryPrice = batteryPricePerUnit*batteryLoad;
        }
        // der Kontostand aendert sich um die Differenz der Kosten und Einnahmen
        ownerCredit += fromOwner*ownerSellPrice - toOwner*ownerBuyPrice; 
        
        // die gesamten Kosten der Kosumenten
        int consumerDebt = directCoverPricePerUnit * directCover + batteryPricePerUnit * fromBattery  + fromOwner*ownerSellPrice; 
        
        // die gesamten Einnahmen der Produzenten
        // beladen der Beatterie wird direkt verguetet auch wenn die energie nicht verkauft wurde
        // nicht ideal, aber das nachhalten wer wie viel Energie in die Batterie geladen hat ist aufwendig 
        // und kommt mit einigen Problemen - moegliche loesung: separate Energiespeicher fuer jeden Produzenten?
        
        int producerCred = directCoverPricePerUnit * (directCover+toBattery) + toOwner*ownerBuyPrice;

    
        // erneutes durchgehen des TeilnehmerArrays um Kosten und Einnahmen proportional zur
        // verbrauchten/erzeugten Energie aufzuteilen
        // bedingungen wie beim ersten mal
        int creditChange = 0;
        for (uint i = 0; i < members.length; i++) {
            
            if (bookKeep[members[i]].matchBlock < bookKeep[members[i]].deletionBlock) {
                if(bookKeep[members[i]].energy < 0) {
                    creditChange = consumerDebt*bookKeep[members[i]].energy/sumCon;
                    // proprtionale Aufteilung der Kosten falls Energie verbraucht wurde
                    bookKeep[members[i]].credit += creditChange;
                }
                if(bookKeep[members[i]].energy > 0) {
                    // proprtionale Aufteilung der Einnahmen falls Energie erzeugt wurde
                    creditChange = producerCred*bookKeep[members[i]].energy/sumPro;
                    bookKeep[members[i]].credit += creditChange;
                }
                
                // die Energie die gematcht wurde entspricht der Energie die zu Beginn im "konto" des Teilnehmers hinterlegt war
                bookKeep[members[i]].matchedEnergy = bookKeep[members[i]].energy;
                
                // aktualisieren des Matchblocks
                bookKeep[members[i]].matchBlock = block.number;
                
                // Ein Event mit einigen Informationen zu dem Match wird ausgegeben
                emit matchEvent(members[i], bookKeep[members[i]].matchedEnergy, creditChange);
            }
        }
        emit generalInfo(directCover, directCoverPricePerUnit, toBattery-fromBattery, batteryLoad, batteryPricePerUnit, toOwner-fromOwner, ownerBuyPrice, ownerSellPrice);
    }
    
 
    function enterEnergy(int enteredEnergy, int sPrice) public {
        
        // falls diese Adresse noch nie Energie "eingezahlt" hat wird sie im Teilnehmer-Array hinterlegt
        if (bookKeep[msg.sender].updateBlock == 0){
            bookKeep[msg.sender].updateBlock = 1;
            bookKeep[msg.sender].deletionBlock = 1;
            members.push(msg.sender);
        }
        // Wenn das letzte Update aelter ist als der letzte Match wird die zuletzt gematchte Energie abgezogen
        if (bookKeep[msg.sender].deletionBlock < bookKeep[msg.sender].matchBlock && bookKeep[msg.sender].matchBlock != block.number){
            bookKeep[msg.sender].energy -= bookKeep[msg.sender].matchedEnergy;
            bookKeep[msg.sender].deletionBlock = block.number;
        }
        
        if (batteryLoad > 0){
            if (sPrice > totalBatteryPrice/batteryLoad){
                sPrice = totalBatteryPrice/batteryLoad-10;
            }
            
        }
        if (sPrice < ownerBuyPrice){
            sPrice = ownerBuyPrice+1;
        }
        if(sPrice > ownerSellPrice){
            sPrice = ownerSellPrice-10;
        }
        // Energiemenge wird um die produzierte/verbrauchte Menge geaendert
        bookKeep[msg.sender].energy += enteredEnergy;
        bookKeep[msg.sender].sellPrice = sPrice;
    
        
        // Event das Energie hinterlegt wurde wird emittet
        emit enterEvent(msg.sender, enteredEnergy, sPrice);
    }
    
    function repairBlockNumbers() public{
        for (uint i = 0; i < members.length; i++){
            if (bookKeep[members[i]].matchBlock == bookKeep[members[i]].deletionBlock){
                bookKeep[members[i]].deletionBlock = block.number;
                bookKeep[members[i]].matchedEnergy = 0;
                bookKeep[members[i]].energy = 0;
            }
        }
    }

    // funktion mit der der "Kontostand" im Smart contract ausgeglichen werden kann
    // der Smart Contract fungiert als "Zwischenhaendler" kann nur Ether auszahlen der im Besitz des Contracts ist
    
    // achtung: typeforce! der credit ist als int definiert um schulden (negativ) darstellen zu koennen. 
    // Ether/Wei-Werte sind immer vom Typ uint! 
    // negative Funds koennen nicht gesendet werden.
    // entsprechnde Checks und Tyoeforces sind daher zu beachten
    function coverCredit() public payable {
        if(msg.sender == owner){
            emit contractPay(owner, int(msg.value), ownerCredit+int(msg.value));
            ownerCredit += int(msg.value);
        }
        else{
            emit contractPay(msg.sender, int(msg.value), bookKeep[msg.sender].credit+int(msg.value));
            bookKeep[msg.sender].credit +=int (msg.value);   
        }
    }
    
    // getter und setter Funktionen
    function getBatteryLoad() view external returns (int){
        return batteryLoad;
    }
    function setBatteryCapacity(int newCap) external {
        batteryCapacity = newCap;
        if (batteryLoad > batteryCapacity){
            totalBatteryPrice = totalBatteryPrice*batteryCapacity/batteryLoad;
            batteryCapacity = batteryLoad;
        }
    }
    function setBatteryLoad(int newLoad) external{
        require (newLoad >=0);
        if (batteryLoad != 0){
            totalBatteryPrice = newLoad/batteryLoad;
        }
        if (newLoad != 0 && batteryLoad == 0){
            totalBatteryPrice = newLoad*ownerSellPrice*10/9;
        }
        batteryLoad = newLoad;
    }
    function setBatteryEff (int8 newEff) external{
        require(newEff < 101 && newEff > 0);
        batteryEfficiency = newEff;
        batteryLoad = 0;
        totalBatteryPrice = 0;
    }
    function setTotalBatPrice (int nPr) external{
        totalBatteryPrice = nPr;
    }
    function getBuyPrice() view external returns (int){
        return ownerBuyPrice;
    }
    function getSellPrice() view external returns (int){
        return ownerSellPrice;
    }
    function setBuyPrice(int newPrice) external {
        require (msg.sender == owner);
        ownerBuyPrice = newPrice;
    }
    function setSellPrice(int newPrice) external {
        require (msg.sender == owner);
        ownerSellPrice = newPrice;
    }
    function getBatteryPricePerUnit() view external returns (int){
        if (batteryLoad != 0){
            return totalBatteryPrice/batteryLoad;
        }
        else{
            return 0;
        }
    }
    function getTotalBatteryPrice() view external returns (int){
        return totalBatteryPrice;
    }
    // Funktion zur Abfrage des eigenen Kontostands
    function getCredit() view external returns(int){
        if (msg.sender == owner){
            return ownerCredit;
        }
        return bookKeep[msg.sender].credit;
    }
    // Funktion zur Abfrage eines spezifischen Kontostands
    function getSpecCredit(address account) view external returns(int){
        if (account == owner){
            return ownerCredit;
        }
        return bookKeep[account].credit;
    }
    // Funktion zur Abfrage des Smart-Contract Kontostands
    function getContractFunds() view external returns (uint) {
        return address(this).balance;
    }
    function setAllCredits(int newCredit) external {
        ownerCredit = newCredit;
        for (uint i = 0; i < members.length; i++){
            bookKeep[members[i]].credit = newCredit;
        }
    }
    function drainContract() external{
        require(msg.sender == owner);
        msg.sender.transfer(address(this).balance);
    }
    function getUpdateBlock(address ofAddr) view external returns (uint){
        return bookKeep[ofAddr].deletionBlock;
    }
    function getMatchBlock(address ofAddr) view external returns (uint){
        return bookKeep[ofAddr].matchBlock;
    }
}