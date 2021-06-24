# HostCLI_RobotArm (última versión 2.3)
**Descripción**</br>
Aplicación Host de control de robots del tipo brazo articulado con 3 grados de libertad.
El aspectos es el de una Interfaz de Línea de Comandos (CLI) que propone una serie de opciones de trabajo típicas.
Los 2 objetivos principales de la aplicación son:
- Permitir realizar pruebas sobre el robot considerando una serie básica de restricciones de operación.
- Servir de interfaz de comunicaciones con otras aplicaciones en redes IP.</br>

Entre sus características se encuentran completado automático de comandos, ayuda en línea para cada comando, incluyendo la sintaxis esperada, así como sintéticos mensajes de estado.
Las letras de estado en la interfaz son:
- S: servidor RPC (indica sí/no se encuentra en ejecución)
- M: motores del robot (indica sí/no se encuentran activos)
- R: estado del robot (indica el grado de preparación del robot)
- T: tarea a realizar por el robot (en caso de encontrarse cargada indica el nombre del archivo asociado)
- RO: es un mensaje variable en función de la operación relizada

* Cambios previstos para versiones futuras del Host
  - Ingresar comandos usando GCode desde la interfaz.
  - Completar funciones RPC propuestas.
  - Opciones para pausar/continuar/detener una tarea.
  - Control de la pinza.
  - Funciones para configurar parámetros de operación generales.
  - Gestión de trayectorias curvas.
  - Gestión de sensores incorporados.
  - Inicio/parada del servidor de streaming (cámara).

**Versiones**
* Host version 2.3 (22jun21)
  - Separación archivo de configuración.
  - Información de estado luego de cada acción en la misma interfaz
  - Uso de colores en la interfaz.

* Host version 2.2 (10abr21)
  - Carga de archivos de tarea con secuencias de operación en formato GCode.
  - Se agrega módulo del servidor RPC

* Host version 2.1 (08mar21)
  - Control entre opciones de menú, incorporando estados de operación del robot.
  - Se agrega opción para la ejecucón de una tarea con prueba básica

* Host version 2.0 (10dic20)
  - Reescritura del código a lenguaje Python 3.
  - Generación de archivo con log de trabajo.

* Host version 1.0 (27ago19)
  - Implementación con operaciones de conexión/desconexión serie, ejecución de rutina de homing, operaciones directas recibiendo GCode.

**Enlaces a recursos asociados**</br>
[Video de demostración]()</br>
[Firmware Robot Arm Community](https://www-20sfactory.com/robot/resource#firmware)</br>
[Archivos 3D y comentarios](https://www.thingiverse.com/puma_3d/designs)</br>
[Definición de API REST]()</br>

**Configuración y Uso**
* Modificar los parámetros de conexión requeridos por el Host en el archivo de configuración puma3d/puma3d_config.py
* Para su lanzamento requiere de python 3 instalado, con los módulos
  - cmd
  - xmlrpc
  - socket
  - traceback
  - logging
  - getopt
  - colorama
* Ejecutar la aplicación mediante
  - (usuario)~$ python3 [directorio de descarga]/Puma3D_robotArm/puma3dhost.py
  - El detalle de las operaciones y eventuales errores producidos se registra en [directorio de descarga]/Puma3D_robotArm/puma3dhost.log
