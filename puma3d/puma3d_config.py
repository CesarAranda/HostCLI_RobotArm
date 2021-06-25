#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Este archivo es parte del paquete Puma3D.
#
# Puma3D es software libre: puede redistribuirlo y/o modificarlo
# según los términos de la Licencia Pública General GNU
# publicada por la Free Software Foundation, ya sea la versión 3 de la Licencia
# o cualquier versión posterior.
#
# Puma3D se distribuye con la esperanza de que sea útil, pero sin garantía alguna,
# inclusive las implícitas por comercialización o compromisos particulares,
# según los términos de la Licencia Pública General GNU.
#
# Consulte la Licencia pública general GNU para obtener más detalles.
# Debería haber recibido una copia de la Licencia Pública General GNU junto con Puma3D.
# Si no es así, vea <http://www.gnu.org/licenses/>.

class P3D_Config():
    """Parametros de conexion del Host"""
    rpc_ip = ''                     # IPv4_del_host
    rpc_port = 7994
    serial_port = '/dev/ttyACM0'    # en Windows COM1, ...
    serial_bauds = 115200
