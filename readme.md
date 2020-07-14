# Elaborato di Programmazione di Reti

## Realizzato Da
* Matteo Alesiani - matteo.alesiani2@studio.unibo.it - 806476
* Tommaso Bailetti - tommaso.bailetti@studio.unibo.it - 889120

## Traccia
Il progetto mira a fornire una possibile soluzione della traccia 1: Server-Router-Client.

## Descrizione Soluzione
La prima entità da eseguire è il Server, il quale attende che altri dispositivi istanzino una connessione.
A seguito è possibile eseguire un'istanza Router.
Una volta collegato al Server, richiede gli indirizzi IP per le interfacce di rete da esso gestite(una verso il Server e l'altra verso i client).
Infine è possibile eseguire istanze Client. Al momento della loro creazione verrà fornita una lista di indirizzi IP relativi a router disponibili all'interno della rete.
Il client sceglierà in quale rete collegarsi e successivamente richiede, attraverso una procedura DHCP semplificata, il proprio indirizzo IP all'interno della rete.
Completata questa fase preliminare, in cui le entità si scambiano informazioni attraverso i collegamenti appositamenti creati, si procede con le funzionalità richieste dalla traccia.
Al client, su propria richiesta, è fornito l'elenco di client con i quali è possibile porre in essere un interscambio di messaggi.
Tali messaggi saranno obbligatoriamente consegnati al Server, il quale verifica l'esistenza della destazione:
* Destinazione trovata: il messaggio prosegue verso la destinazione passando attraverso il router apposito
* Destinazione NON trovata: il messaggio ritorna al mittente, al quale viene comunicato che il destinatario non esiste.

Al fine di garantire il corretto funzionamento, i client, quando escono della rete, devono comunicarlo al server.
