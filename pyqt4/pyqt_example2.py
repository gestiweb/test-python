#!/usr/bin/env python
# encoding: UTF-8

# ::::::::::::: Ejemplo básico 2 de PyQt4 ::::::::::::

import os.path
# La librería os.path contiene las funciones necesarias para tratar rutas 
# del sistema operativo de forma compatible y multiplataforma

import sys
from PyQt4 import QtGui, QtCore, uic

# Las siguientes funciones son ayudas para hallar la ruta de este mismo fichero
# o de la aplicación en sí misma. 
def apppath(): return os.path.abspath(os.path.dirname(sys.argv[0]))
def filepath(): return os.path.abspath(os.path.dirname(__file__))

print filepath()

def appdir(x): # convierte una ruta relativa a la aplicación en absoluta
    if os.path.isabs(x): return x
    else: return os.path.join(apppath(),x)
def filedir(x): # convierte una ruta relativa a este fichero en absoluta
    if os.path.isabs(x): return x
    else: return os.path.join(filepath(),x)
    
# El motivo de usar estas funciones es que, si usamos rutas relativas (por 
# ejemplo, ./example2.ui) son relativas no al fichero ni a la aplicación, sino
# relativas a la carpeta de trabajo. Eso significa que apuntan a sitios 
# distintos cuando la aplicación es lanzada desde distintas rutas.

# por ejemplo, en este caso ejecutaríamos desde la misma carpeta:
# 
# gestiweb:~/Dropbox/Documentos/Docum$ cd source_code 
# gestiweb:~/Dropbox/Documentos/Docum/source_code$ cd pyqt_example 
# gestiweb:~/Dropbox/Documentos/Docum/source_code/pyqt_example$ python pyqt_example2.py
#
# pero también podemos hacerlo desde la carpeta padre:
#
# gestiweb:~/Dropbox/Documentos/Docum/source_code/pyqt_example$ cd ..
# gestiweb:~/Dropbox/Documentos/Docum/source_code$ python pyqt_example/pyqt_example2.py
#
# si no tuvieramos esto en cuenta podemos encontrarnos con un error como este:
#
# IOError: [Errno 2] No existe el fichero o el directorio: 'example2.ui'


app = QtGui.QApplication(sys.argv) # Creamos la entidad de "aplicación"

ui_filepath = filedir("example2.ui") # convertimos la ruta a absoluta
print "Loading UI FILE: '%s' . . . " % ui_filepath
window = uic.loadUi(ui_filepath) # Cargamos un fichero UI externo
# y nos devuelve el objeto listo para usar.
print "done."

window.show() # el método show asegura que se mostrará en pantalla.

retval = app.exec_() # ejecutamos la aplicación. A partir de aquí perdemos el

sys.exit(retval) # salimos de la aplicación con el valor de retorno adecuado.

