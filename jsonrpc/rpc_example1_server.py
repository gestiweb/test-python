# encoding: UTF-8
# ::::::::::::: Ejemplo básico 1 de json-rpc (SERVIDOR) ::::::::::::

from bjsonrpc.handlers import BaseHandler
# importamos BaseHandler, que es la clase base que va a permitirnos definir
# métodos que se pueden ejecutar remotamente.

from bjsonrpc import createserver
# importamos la función createserver, que es una forma rápida para poner el 
# servidor en marcha.

import time
# la librería time nos provee de funciones básicas de hora. Es útil para las 
# pruebas (para enviar por ejemplo la hora actual, etc).

class Chronometer(BaseHandler):
    """
        Ejemplo básico de cronómetro remoto. Se puede iniciar, detener
        y consultar el tiempo transcurrido.
    """
    def _setup(self):  
        """ 
            _setup es la función que se lanza la primera vez para inicializar
            los valores. Hay que tener en cuenta que cada conexión tiene su
            instancia separada.
        """
        self._begin = 0 # momento de inicio de crono
        self._end = 0   # momento de fin del crono
        self._state = 0 # 0 is off, 1 is on.

    def begin(self): 
        """
            devuelve el momento en que se inició el crono o 0
        """
        return self._begin
        
    def end(self): 
        """
            devuelve el momento en que se detuvo el crono o la hora actual.
        """
        if self._state == 0: return self._end
        else: return time.time()
            
    def start(self):
        """
            pone en marcha el cronómetro.
        """
        self._begin = time.time()
        self._state = 1
    
    def stop(self):
        """
            detiene el cronómetro.
        """
        self._end = time.time()
        self._state = 0
        
    def lapse(self):
        """
            devuelve la cantidad de tiempo en segundos que ha pasado
            desde el inicio del crono hasta su fin 
            (o hasta ahora si no ha parado)
        """
        return self.end() - self.begin()

    def stoplapse(self,arg1):
        self.stop()
        return self.lapse()
        

s = createserver(handler_factory=Chronometer) # creamos el servidor
# handler_factory especifica qué objeto es que se crea con cada conexión.
# por defecto escucha en "127.0.0.1" pero se puede definir con host=".."
# por defecto el puerto es el 10123 pero se puede cambiar con port=123

s.debug_socket(True) # Esto indica que debe imprimir por pantalla lo que
# se envía y se recibe por el socket. Es útil para entender cómo funciona el 
# protocolo.

s.serve() # empieza el bucle infinito de servicio. Sale de la función en cuanto
# se tenga que detener el programa. Normalmente por fallo inesperado o porque
# se recibe una señal de detener (SIGINT, SIGTERM) del sistema operativo.


