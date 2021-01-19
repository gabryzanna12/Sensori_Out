#######################################################################
#               Scritto da ZANNI Gabriele in Python 3.9               #
#         - Rilevazione simulata di dati dai sensori di un silos.     #
#         - Invio tramite protocollo mqtt.                            #
#         - Controllo e trasmissione errori.                          #
#######################################################################

import paho.mqtt.client as mqtt #Installabile con: pip install paho.mqtt
from time import sleep
from random import random

# classe base simulazione Sensore
# attributi:
#    client -> Si passa l'oggetto del client mqtt per permettere la pubblicazione dei dati.
#    topic  -> Stringa contenente il topic mqtt sul quale il sensore trasmette i dati.
#    max    -> Valore intero rappresentante la rilevazione massima ottenibile dalla simulazione del sensore.
class Sensore():
    # Costruttore
    def __init__(self, client, topic, max):
        self.client = client
        self.topic = topic
        self.max = max
        print("Sensore creato:\n\tTopic: {0}\n\tValore massimo: {1}".format(self.topic, self.max)) #Console debugging

    def inviaDati(self):
        self.rilevazione = round(random()*self.max, 2)
        client.publish(self.topic, self.rilevazione)
        print("Dato Inviato:\n\tTopic: {0}\n\tDato: {1}".format(self.topic, self.rilevazione))

    # Facoltativamente si può richiamare la funzione 'avviso' e definire parametri oltre i quali vengono trasmessi messaggi di errore.
    def avviso(self, attenzione, allarme):
        if self.rilevazione > allarme:
            self.client.publish(self.topic+"_warn", "ATTENZIONE: " + self.topic)
            print("Avviso Inviato: ATTENZIONE: " + self.topic)

        elif self.rilevazione > attenzione:
            self.client.publish(self.topic+"_warn", "ERRORE: " + self.topic)
            print("Avviso Inviato: ERRORE: " + self.topic)

        else:
            self.client.publish(self.topic+"_warn", "OK: " + self.topic)
            print("Avviso Inviato: OK: " + self.topic)



# Configurazione
CLIENT_NAME = "sensori_mqtt_client"
HOST = "example.com"
PORT = 1883
TICK = 10 # in secondi, cadenza di rilevazione e invio dei valori.


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connesso correttamente:\n\tCodice: {0}\n\tNome client: {1}\n\tHost: {2}\n\tPorta: {3}\n\tTick: {4}".format(rc, CLIENT_NAME, HOST, PORT, TICK))
    else:
        print("Errore connessione:\n\tCodice: {0}\n\tNome client: {1}\n\tHost: {2}\n\tPorta: {3}\n\tTick: {4}".format(rc, CLIENT_NAME, HOST, PORT, TICK))

# Creazione e connessione client mqtt
client = mqtt.Client(CLIENT_NAME)
client.on_connect = on_connect
client.connect(HOST, port=PORT, keepalive=60, bind_address="")

### Creazione sensori ###

# Sensori esterni
temp_est = Sensore(client, "temperatura_esterna_out_gz", 400)
um_est = Sensore(client, "umidita_esterna_out_gz", 100)
press_est = Sensore(client, "pressione_esterna_out_gz", 10)

# Sensori temperatura interna
temp_int = []
for i in range(10):
    temp_int.append(Sensore(client, "temperatura_interna" + str(i+1) + "_out_gz", 400))

# Sensori umidità interna
um_int = []
for i in range(10):
    um_int.append(Sensore(client, "umidita_interna" + str(i+1) + "_out_gz", 400))

# Sensori pressione interna
press_int = []
for i in range(10):
    press_int.append(Sensore(client, "pressione_interna" + str(i+1) + "_out_gz", 400))

# Sensori velocità miscelatori
vel_misc = []
for i in range(3):
    vel_misc.append(Sensore(client, "velocita_miscelatore" + str(i+1) + "_out_gz", 500))  # velocita_miscelatore1_out_gz

vel_misc.append(Sensore(client, "velocita_miscelatore_alto_out_gz", 500))
vel_misc.append(Sensore(client, "velocita_miscelatore_basso_out_gz", 500))

# Sensori pressione iniettori
press_iniett = []
for i in range(5):
    for j in range(3):
        press_iniett.append(Sensore(client, "pressione_iniettore" + str(i+1) + "_" + str(j+1) + "_out_gz", 20))

### FINE: Creazione sensori ###

### Loop infinito: Invio dati - Impostazione avvisi ###
while True:
    print("\n##########################")
    print("# Aspettando {0} Secondi #".format(TICK))
    print("##########################\n")
    sleep(TICK)
    
    # Sensori esterni
    temp_est.inviaDati()
    temp_est.avviso(300, 350)
    um_est.inviaDati()
    um_est.avviso(80, 90)
    press_est.inviaDati()
    press_est.avviso(8, 9)

    # Temperatura interna
    for temp in temp_int:
        temp.inviaDati()
        temp.avviso(300, 350)

    # Umidità interna
    for um in um_int:
        um.inviaDati()
        um.avviso(80, 90)

    # Pressione interna
    for press in press_int:
        press.inviaDati()
        press.avviso(8, 9)

    # Velocità miscelatori
    for vel in vel_misc:
        vel.inviaDati()

    # Pressione iniettori generatori
    for press in press_iniett:
        press.inviaDati()
        press.avviso(17, 18)
