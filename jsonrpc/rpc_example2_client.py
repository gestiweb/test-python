#!/usr/bin/env python
# encoding: UTF-8

# ::::::::::::: Ejemplo básico 2 de JSON-RPC (cliente) + PyQt4 ::::::::::::

# ** Necesita una versión bastante reciente de BJSON-RPC, al menos la versión
# 0.1.2 (aún no publicada). Ver rama master del repositorio GIT.

import os.path

import sys
from PyQt4 import QtGui, QtCore, uic
from bjsonrpc import connect
from bjsonrpc.handlers import BaseHandler 
from bjsonrpc.exceptions import ServerError 
# Importamos ServerError para poder capturar los errores que reporta el servidor

# funciones de ayuda para hallar rutas de fichero relativas
def apppath(): return os.path.abspath(os.path.dirname(sys.argv[0]))
def filepath(): return os.path.abspath(os.path.dirname(__file__))

def appdir(x): # convierte una ruta relativa a la aplicación en absoluta
    if os.path.isabs(x): return x
    else: return os.path.join(apppath(),x)
def filedir(x): # convierte una ruta relativa a este fichero en absoluta
    if os.path.isabs(x): return x
    else: return os.path.join(filepath(),x)

# En este cliente tenemos también un "handler" como en el servidor. Aquí
# ubicamos los métodos que el servidor puede llamar al cliente. Esto es 
# lo que llamamos "bidireccionalidad". Lo usaremos para que el servidor
# nos avise de que hay material nuevo, en lugar de preguntar cada vez.
# Una versión simplificada del programa podría usar un Timer de 500ms 
# para preguntar si hay cambios al servidor de forma regular.
class ClientChatter(BaseHandler):
    def _setui(self, ui):
        """
            Permite asociar la instancia con el formulario, para poder modificar
            variables del formulario desde aquí.
        """
        self.ui = ui
        
    def needs_update(self):
        """
            Función que llamará el servidor cuando haya que actualizar. Nosotros
            cambiaremos un flag para advertir al timer que debe actualizar.
            No se nos informa de qué ha cambiado, por lo que se actualizará 
            todo.
        """
        self.ui.to_be_updated = True



class ConnectionDialog(QtGui.QDialog):
    """
        diálogo de conexión. la aplicación se iniciará con este diálogo, que 
        contiene los parámetros Host, Port y el botón de conectar.
        
        El único trabajo que realiza este formulario es recoger esos datos y la
        acción. Cuando se clica conectar, creará el diálogo de chat, y será este
        , en última instancia, el que realice la conexión.
    """
    chatwindows = [] # variable de clase estática (es común a todas las instancias)
    """ lista que contiene los distintos diálogos lanzados. sirve únicamente para
        evitar que python libere la memoria de los diálogos nada más crearlos, 
        ya que salen fuera del scope. """
        
    def __init__(self):
        """ construcción del diálogo. simplemente llamar a la función superior,
            configurar la interfaz y conectar la señal del botón a nuestra
            función. """
        QtGui.QDialog.__init__(self)
        self.setup_ui()
        # conectar el botón btnConnect a nuestra función:
        self.connect(self.ui.btnConnect, QtCore.SIGNAL("clicked()"),
                    self.connect_clicked)
            
    def setup_ui(self):
        """ abre el fichero deseado y lo carga como interfaz. Esta función
        sólo se puede llamar una vez en la vida del diálogo. """
        ui_filepath = filedir("example2_connection.ui") # convertimos la ruta a absoluta
        self.ui = uic.loadUi(ui_filepath,self) # Cargamos un fichero UI externo    
    
    def connect_clicked(self):
        """ acción a realizar cuando se pulsa el botón de conectar. """
        chat = ChatDialog(host=str(self.ui.host.text()),port=int(self.ui.port.value()))
        self.chatwindows.append(chat) # agregamos la nueva ventana al listado.
        chat.show()
        #self.close()  
        """ ^- esta línea, si está habilitada, hace que se cierre
         el diálogo de conectar una vez arrancado el chat. """
 

class ChatDialog(QtGui.QDialog):
    """ diálogo de chat. cuando se abre se conecta al host y puerto especificado.
        
        Algunos aspectos pueden ser especialmente confusos aquí:
            * La lectura de los mensajes nuevos en el servidor es diferencial:
            al servidor se le pide desde qué mensaje queremos recibir. Para saber
            qué mensajes ya hemos descargado, se mira directamente la cantidad
            de mensajes (items) en pantalla. Pero como hay mensajes que son 
            "locales", esos se han de restar. Para eso aparece "extracount", una
            variable que almacena cuantos mensajes de pantalla no son realmente
            del servidor. Por supuesto, existen otras formas más elegantes (y
            laboriosas) de conseguir lo mismo.
            
            * La actualización de los contenidos se lleva a cabo mediante un
            mensaje del servidor al cliente. Esto es uan técnica bastante común
            para ahorrar ancho de banda con peticiones constantes. No obstante,
            trae algunos problemas. El principal, es que las notificaciones, 
            aunque se manden en el momento indicado, no son procesadas 
            instantáneamente. El motivo es que se ha de leer regularlmente el
            socket TCP/IP para que nos lleguen los datos. De lo contrario quedan
            encolados. Es por eso que, a pesar de que es el servidor el que 
            notifica, hemos de estar revisando constantemente si nos ha llegado
            algo con un timer. De lo contrario, nos llegaría la notificación en
            el momento en que intentáramos enviar algo. El objeto de este 
            sistema, es conseguir un ancho de banda reducido y no es primordial
            evitar el uso de CPU con el timer. Existen otros métodos que podrían
            ahorrar también CPU, pero sencillamente son más complejos de entender.
            Además, entendemos que la CPU usada por una llamada cada 100ms es
            muy poca y no es algo importante.
    """
    def __init__(self,host="127.0.0.1",port=10123):
        QtGui.QDialog.__init__(self)
        ui_filepath = filedir("example2_chat.ui") # convertimos la ruta a absoluta
        self.ui = uic.loadUi(ui_filepath,self) # cargamos un fichero UI externo    

        self.to_be_updated = True # Indica que debe consultar los nuevos cambios
        self.extracount = 0       # Indica qué delta ha de usar al descargar el log de mensajes
        """ creamos las propiedad antes de que puedan ser usadas. """
        
        # Conectar el botón send
        self.connect(self.ui.btnSend, QtCore.SIGNAL("clicked()"),
                    self.btnSend_clicked)
                    
        # Creamos los dos iconos que usaremos en este diálogo repetidamente:
        self.img_people = QtGui.QIcon(QtGui.QPixmap(filedir("people.png"),"png"))
        self.img_user = QtGui.QIcon(QtGui.QPixmap(filedir("user.png"),"png"))
        
        # Conectamos al servidor remoto. Al pasar el parámetro handler_factory
        # estamos abriendo la puerta a que el servidor remoto llame nuestras
        # funciones.
        self.remote = connect(handler_factory=ClientChatter, host=host,port=port)
        self.remote.handler._setui(self) # enlazamos este formulario con la instancia de RPC.
        
        # Creamos un timer nuevo que revisará cuando hay novedades.
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timer_timeout)
        self.timer.setInterval(100) # establecemos el intervalo de llamada a 100 milisegundos.
        self.timer.start()       
        
    def closeEvent(self,event):
        """
            cierra correctamente la ventana. Principalmente detiene el timer
            para que no use la conexión y luego la cierra.
            Si no se hiciera esto, el formulario queraría realmente "escondido"
            pudiendo ser mostrado más tarde.
        """
        self.timer.stop()       
        self.remote.close()
        
        ConnectionDialog.chatwindows.remove(self) # Liberar la memoria.
        event.accept()
        
    def update_userlist(self):
        """ función de actualizar lista de usuarios. No es diferencial, sino 
        completo. Borra el listado, pide la nueva lista y la vuelve a llenar.
        En esta misma función obtenemos el nick actual y lo usamos para cambiar
        el icono a nuestro usuario.
        """
        self.ui.lstUsers.clear() # borrar todos los usuarios
        userlist = self.remote.call.get_userlist() # obtener la nueva lista
        self.username = self.remote.call.whoami() # obtener nuestro nombre de usuario
        self.ui.lblUser.setText(self.username) # poner nuestro nombre en el label
        
        for user in sorted(userlist): # para cada usuario en la sala (ordenado alfabéticamente):
            if self.username == user: 
                icon = self.img_people # Para nuestro usuario ponemos el icono people.png
            else:
                icon = self.img_user # para el resto user.png
            
            item = QtGui.QListWidgetItem(icon,user) # creamos la entrada nueva
            if self.username == user: 
                # cambiar el color de la letra a azul si es nuestro nick
                item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 250))) 
            
            self.ui.lstUsers.addItem(item) # finalmente, insertar.
            
    def update_chat(self):
        """ actualiza diferencialmente las nuevas entradas del chat. Calcula
        cual fue la ultima entrada descargada en función de la cantidad de items
        que ya hay en a lista y cuantos de éstos son mensajes internos."""
        from_id = self.ui.lstChat.count() - self.extracount # Calcula el punto inicial de descarga
        new_chats = self.remote.call.get_queue(from_id) # pide al servidor los nuevos mensajes
        for chat in new_chats:
            item = QtGui.QListWidgetItem(unicode(chat))
            if chat.startswith(" -*-"): # si inicia con -*- es un mensaje de sistema
                item.setForeground(QtGui.QBrush(QtGui.QColor(120, 120, 120)))
            else:
                item.setForeground(QtGui.QBrush(QtGui.QColor(120, 50, 50)))
                if chat.startswith(self.username+":"): # si inicia con "usuario:" es un comentario nuestro
                    item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                elif chat.find(self.username) > 1: # nos han nombrado.
                    item.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 210)))
                    
            self.ui.lstChat.addItem(item)
        # Seleccionamos el último registro para asegurar que sea visible.
        self.ui.lstChat.setCurrentRow(self.ui.lstChat.count()-1)
        
   
    def timer_timeout(self):
        try:
            # Comprobamos si hay algo pendiente de leer en la conexión.
            self.remote.dispatch_until_empty() 
        except Exception,e: # esperamos posibles errores.
            # Muy a menudo en la gestión de las redes aparecen errores de timeout
            # y similares, y son completamente normales. Debemos ignorarlos.
            
            # TODO: sería mejor ignorar sólo los errores de red.
            print "**", e
            
        if self.to_be_updated: # Si se ha marcado que existe una actualización:
            # pasamos el flag a false para que no entre de nuevo
            self.to_be_updated = False 
            self.update_userlist() # actualizar usuarios
            self.update_chat() # actualizar chat
                
    
    def btnSend_clicked(self):
        """
            envía el mensaje cuando se pulsa Send. Si el mensaje empieza por /
            entonces entiende que es un comando interno.
        """
        try:
            text = unicode(self.ui.txtSend.text())
            if not text: return 
            if text[0] == '/':
                comm = text[1:].split(" ")
                ret = self.remote.call.command(comm[0],comm[1:])
                if ret:
                    item = QtGui.QListWidgetItem(self.img_people,unicode(ret))
                    item.setBackground(QtGui.QBrush(QtGui.QColor(235, 235, 250)))
                    self.ui.lstChat.addItem(item)
                    self.extracount += 1
                    self.ui.lstChat.setCurrentRow(self.ui.lstChat.count()-1)
                
            else:
                self.remote.call.post(text) # enviar mensaje
            self.ui.txtSend.setText("") # si todo funciona, limpiamos la casilla.
        except ServerError, e: # cualquier error remoto es reportado al usuario:
            item = QtGui.QListWidgetItem(self.img_user,u"ERROR: " + unicode(e.args[0]))
            item.setBackground(QtGui.QBrush(QtGui.QColor(250, 215, 210)))
            self.ui.lstChat.addItem(item)
            self.extracount += 1
            self.ui.lstChat.setCurrentRow(self.ui.lstChat.count()-1)

def main():                     
    app = QtGui.QApplication(sys.argv) # Creamos la entidad de "aplicación"

    connwindow = ConnectionDialog()
    connwindow.show() # el método show asegura que se mostrará en pantalla.

    retval = app.exec_() # ejecutamos la aplicación. A partir de aquí perdemos el

    sys.exit(retval) # salimos de la aplicación con el valor de retorno adecuado.

if __name__ == '__main__': main()