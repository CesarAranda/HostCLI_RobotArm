# HostCLI_RobotArm (última versión 2.3)
**Descripción**

Aplicación y Host RPC para control de robots del tipo brazo articulado con 3 grados de libertad.

Si bien se toma como base el robot propuesto por F.Tobler controlado por el firmware ofrecido por 20sfffactory (ver enlaces más abajo), el software es extensible a otros robots y drivers similares.

El aspecto general es el de una Interfaz de Línea de Comandos (CLI) para su uso mediante consola.

Los 2 objetivos principales de la aplicación son:
- Permitir realizar pruebas sobre el robot considerando una serie básica de restricciones de operación.
- Servir de interfaz de comunicaciones con otras aplicaciones en redes IP.

Entre otros detalles de funcionalidad se destacan el completado automático de comandos, historial de comandos que facilita la repetición de órdenes anteriores, la ayuda en línea para cada comando (incluyendo la sintaxis esperada), y la presencia de información breve de estado, asociados a letras visibles en la interfaz:
- S: servidor RPC (indica sí/no se encuentra en ejecución),
- M: motores del robot (indica sí/no se encuentran activos),
- R: estado del robot (indica el grado de preparación del robot),
- T: estado de una tarea (secuencia de órdenes GCode a realizar por el robot),
- A: en caso que una tarea se encuentre "cargada" indica el nombre del archivo correspondiente,
- RO: es un mensaje variable en función de la operación realizada.

Los cambios previstos para próximas versiones del Host:
- Ingresar comandos usando GCode desde la interfaz.
- Completar funciones RPC propuestas.
- Opciones para pausar/continuar/detener una tarea.
- Control de la pinza.
- Funciones para configurar parámetros de operación generales.
- Gestión de sensores incorporados.
- Inicio/parada del servidor de streaming (cámara).
- Gestión de trayectorias curvas (previa actualización del firmware).

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
  - Se agrega opción CLI para la ejecución de una tarea con prueba básica (fija)

* Host version 2.0 (10dic20)
  - Reescritura del código a lenguaje Python 3.
  - Generación de archivo con log de trabajo.

* Host version 1.0 (27ago19)
  - Implementación con operaciones de conexión/desconexión serie, ejecución de rutina de homing, ejecución de operaciones GCode directas usando comandos en formato propietario.

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

**Enlaces a recursos asociados**</br>
[Video de demostración](https://youtu.be/gu-gkutfFFo)</br>
[Definición de la API REST del SaaS](https://www.getpostman.com/collections/0dbea506963e85d836dc)</br>
[Firmware Robot Arm Community](https://www-20sfactory.com/robot/resource#firmware)</br>
[Robot ampliado y comentarios de ensamblado](https://www.thingiverse.com/thing:3674358)</br>
[Robot de base](https://www.thingiverse.com/thing:1718984)</br>
