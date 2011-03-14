# encoding: UTF-8
# ::::::::::::: Ejemplo básico 1 de json-rpc (CLIENTE) ::::::::::::

from bjsonrpc import connect
import time
c = connect()
c.call.start() # iniciamos el cronómetro
a = 0
# realizamos algunas operaciones al azar, costosas...
for i in range(1000):
    a += i 
res = c.method.stoplapse()

# y preguntamos el tiempo transcurrido:
print "Elapsed:", c.call.lapse()
print res.value()
time.sleep(0.1) # dejamos que pase una decima de segundo mas...
c.call.stop() # y detenemos el cronómetro

# preguntamos el tiempo transcurrido: (habrá pasado aprox. 0.1 segundos)
print "Elapsed:", c.call.lapse()

time.sleep(0.1) # dejamos que pase otra decima de segundo. 

# el cronometro está parado. No debe haber diferencia de tiempo:
print "Elapsed:", c.call.lapse() # debe valer lo mismo que el anterior.

"""
    La salida normal de este programa es aproximadamente ésta:
    
        Elapsed: 0.00327587127686
        Elapsed: 0.104089021683
        Elapsed: 0.104089021683
        
    --------------    
    
    En la parte del servidor, si tenemos debug_socket activado, veremos:
    
        >:25: {"method":"start","id":1}
        <:35: {"id":1,"result":null,"error":null}
        >:25: {"method":"lapse","id":2}
        <:52: {"id":2,"result":0.0032758712768554688,"error":null}
        >:24: {"method":"stop","id":3}
        <:35: {"id":3,"result":null,"error":null}
        >:25: {"method":"lapse","id":4}
        <:50: {"id":4,"result":0.10408902168273926,"error":null}
        >:25: {"method":"lapse","id":5}
        <:50: {"id":5,"result":0.10408902168273926,"error":null}
        
    Donde:
        - > o < (mayor que, menor que) indica el sentido de la trama.
            > (mayor que) indica que es una trama de cliente -> servidor
            < (menor que) indica que es una trama de servidor -> cliente
        - :99: indica el número de bytes usados por la trama.
        el resto de carácteres son la trama enviada o recibida.
        
        Para más información sobre el protocolo:
        http://en.wikipedia.org/wiki/JSON-RPC

"""
