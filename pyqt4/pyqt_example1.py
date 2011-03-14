#!/usr/bin/env python
# encoding: UTF-8

# ::::::::::::: Ejemplo básico de PyQt4 ::::::::::::

# La primera linea del fichero es conocida como "shebang". Hace que el programa
# pueda ser marcado como ejecutable. Shebang son los dos primeros carácteres #!
# y indican a UNIX que el programa se ejecuta pasándolo como parámetro a un 
# intérprete. UNIX lee la primera línea del fichero para saber qué programa
# debe de usar. Se puede poner a lo sumo un argumento adicional.

# La segunda línea del fichero es el encoding (codificación) y es *obligatoria*
# si no se pone codificación se asume ASCII y por tanto cualquier acento en el
# fichero *aunque esté como comentario* será motivo de error al arrancar el 
# programa.

# Generalmente los ficheros los subimos en UTF-8 y indentado a 4 espacios.


import sys 
# La librería "sys" es la que maneja aspectos relacionados con el sistema 
# operativo de un modo genérico. La usamos para dos cosas: para poder devolver
# el valor de retorno de la aplicación en sys.exit(retval) y para leer los
# argumentos de entrada por consola.


from PyQt4 import QtGui, QtCore
# PyQt4 es la librería que enlaza Python con Qt4. Existe otra librería similar
# llamada PySide, pero PyQt4 es más antigua y común. Generalmente programar
# con una o con la otra es idéntico, así que al menos inicialmente, programaremos
# en PyQt4 porque será más facil para todos instalar esta librería.

# QtGui es el módulo de Qt encargado de los formularios, controles, gráficos...
# .. generalmente todo lo que tiene que ver con el entorno gráfico está aquí.

# QtCore es el encargado de el núcleo común de Qt y lleva cosas internas que no 
# están relacionadas con gráficos, como por ejemplo las señales y los slots.
# ... en este programa de ejemplo no se usa QtCore, pero lo dejamos porque
# suele usarse bastante, como recordatorio.


app = QtGui.QApplication(sys.argv) # Creamos la entidad de "aplicación" a partir
# de los argumentos de entrada. Esto permite a Qt parsear los switches que les
# podemos pasar a nuestros programas.

window = QtGui.QDialog() # Creamos una ventana de ejemplo, un diálogo.
window.show() # el método show asegura que se mostrará en pantalla.

retval = app.exec_() # ejecutamos la aplicación. A partir de aquí perdemos el
# control de la aplicación y lo pasamos a Qt. Desde este punto la aplicación 
# es de tipo event-driven. La función retorna cuando el programa ha terminado.

# el programa terminará cuando no queden ventanas de la aplicación creadas
# o cuando un elemento en el código fuente lance algún tipo de instrucción
# de finalización de la aplicación.

sys.exit(retval) # salimos de la aplicación con el valor de retorno adecuado.

# El valor de retorno puede servir para que un programa externo sepa si este
# programa ha fallado en su ejecución.

