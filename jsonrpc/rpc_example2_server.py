# encoding: UTF-8
# ::::::::::::: Ejemplo básico 2 de json-rpc (SERVIDOR) ::::::::::::

from bjsonrpc.handlers import BaseHandler
from bjsonrpc import createserver

import time,random
import re

class Chatter(BaseHandler):
    """
        Ejemplo básico de servidor de chat. 
    """
    _usernames = [] # lista de usuarios conectados.
    _message_queue = [" -*- welcome to bjsonrpc chatter -*- "] # log de mensajes
    _clients = [] # lista de clientes conectados al servidor.
    
    def _setup(self):  
        """
            Configuración inicial al conectar un nuevo cliente:
            * Crearle un nuevo nick no usado
            * Asociar los comandos disponibles
            * Anotar el cliente en la lista
            * Enviar un mensaje informando que el usuario se ha unido
        """
        self._username = None
        self._commands = {
            'nick' : self.set_username
        }
        self._to_update = False
        self._clients.append(self)
        self.set_random_username()
        self._post(u" -*- User '%s' has joined -*- " % self._username)
    
    def _update(self):
        """ función para simplificar la notificación de cambios a todos los 
            clientes. usa la lista de clientes para llamar a sus funciones. 
            Por tanto, diríamos que indirectamente un cliente está llamando a 
            otro cliente, o al menos provocando la llamada.
        """
        for client in self._clients:
            client._to_update = True
            try:
                # la llamada se debe realizar con notify en lugar de call.
                # notify no espera respuesta. Si no fuese así, el programa se 
                # congelaría esperando a que todos los clientes respondan.
                client._conn.notify.needs_update()
            except Exception, e: 
                # de los pocos errores que pueden aparecer aquí es que
                # el cliente no tenga su conexión aún completamente inicializada.
                print "Error trying to ping remote client:" , e
    
    def _shutdown(self):
        """ función que se llama automáticamente cuando un cliente se desconecta.
            Se envía un mensaje y se limpian algunos listados.
        """
        self._post(u" -*- User '%s' has quit -*- " % self._username)
        self._clients.remove(self)
        if self._username:
            self._usernames.remove(self._username)
            self._update()
        BaseHandler._shutdown(self) # hay que recordar llamar a la función superior
    
    def set_random_username(self):
        """
            asigna un nombre de usuario al azar.
        """
        if self._username:
            self._usernames.remove(self._username)
        self._username = "guest%04X" % random.randint(0,0xFFFF)
        if self._username in self._usernames: self.setRandomUsername()
        else:
            self._usernames.append(self._username)
            self._update()
    
    def get_queue(self,from_id = 0, to_id = None):
        """
            envía un trozo deseado de la cola. Notese que si uno de los argumentos
            es None, sería lo mismo que no especificarlo en el slice.
        """
        return self._message_queue[from_id:to_id]
        
    def _post(self,message):
        """
            función interna de envío de mensaje.
        """
        self._message_queue.append(unicode(message))
        self._update()
    
    def post(self,message):
        """
            función pública de envío de mensaje. Incluye el nombre del usuario.
        """
        self._post(u"%s: %s" % (self._username,unicode(message)))
    
    def command(self, cname, args):
        """
            función de llamada a comandos especiales. Toma la función del 
            diccionario y la llama con los argumentos deseados.
        """
        if cname not in self._commands: raise ValueError, "%s is not a valid command" % cname
        return self._commands[cname](*args)
    
    def set_username(self,name):
        """
            cambiar el nombre de usuario. Comprobamos que siga un patrón 
            bien definido.
        """
        if name in self._usernames: raise ValueError, "username '%s' already taken!" % name
        if not re.match("^[a-z]{2}[a-z0-9]+$",name): raise ValueError, "username '%s' is invalid (must be a-z,0-9; at least 3 chars and starting with 2 letters)!" % name
        if len(name) > 8: raise ValueError, "username '%s' is too long! (maximum 8 characters)" % name
        if self._username:
            self._usernames.remove(self._username)
        self._post(u" -*- User '%s' is now known as '%s' -*- " % (self._username, name))
            
        self._username = name
        self._usernames.append(self._username)
        self._update()
        return "Username changed to '%s'" % self._username
    
    def get_userlist(self):
        """
            leer los nombres de los usuarios.
        """
        return self._usernames
    
    def whoami(self):
        """
            obtener el nombre de usuario para esta conexión.
        """
        return self._username
        
    

s = createserver(handler_factory=Chatter, host="0.0.0.0") # creamos el servidor

s.debug_socket(True) # imprimir las tramas enviadas y recibidas.

s.serve() # empieza el bucle infinito de servicio. 


