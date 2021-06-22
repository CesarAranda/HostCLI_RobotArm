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
# inclusive las implícitas por comercialización o compromisos particulares.
#
# Consulte la Licencia pública general GNU para obtener más detalles.
# Debería haber recibido una copia de la Licencia Pública General GNU junto con Puma3D.
# Si no es así, vea <http://www.gnu.org/licenses/>.

import sys
import traceback
import logging
import getopt
from colorama import Cursor, init, Fore, Style
from puma3d.puma3d_info import P3D_Info
from puma3d.puma3d_hostcli import P3D_HostCLI

if __name__ == "__main__":


    usage = "Uso:\n"+\
            "  puma3d_hostcli [OPTIONS] [FILE]\n\n"+\
            "Options:\n"+\
            "  -h, --help\t\tMuestra este mensaje y termina\n"+\
            "  -V, --version\t\tMuestra el número de versión del programa y termina\n"+\
            "  -I, --info\t\tMuestra datos generales relacionados al programa y termina\n"

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hIV', ['help', 'info', 'version'])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage)
        sys.exit(2)
    init(autoreset=True)
    f1 = Style.BRIGHT + Fore.BLUE
    f2 = Fore.WHITE
    for op, ar in opts:
        print(op)
        if op in ('-V','--version'):
            print( P3D_Info.name + ': ' + P3D_Info.version)
            sys.exit(0)
        elif op in ('-I', '--info'):
            print(f1 + 'Aplicación:    ' + f2 + P3D_Info.name)
            print(f1 + 'Descripción:   ' + f2 + P3D_Info.description)
            print(f1 + 'Versión:       ' + f2 + P3D_Info.version)
            print(f1 + 'Fecha rev.:    ' + f2 + P3D_Info.date)
            print(f1 + 'Robot de base: ' + f2 + P3D_Info.robot)
            print(f1 + 'Con firmware:  ' + f2 + P3D_Info.driver)
            print(f1 + 'Autor:         ' + f2 + P3D_Info.author + f1 + ' [alias: ' + f2 + P3D_Info.alias + f1 + ']')
            print(f1 + 'Perfil:        ' + f2 + P3D_Info.linkedlin)
            print(f1 + 'Impresión 3D:  ' + f2 + P3D_Info.thingiverse)
            print(f1 + 'Software GNU:  ' + f2 + P3D_Info.github)
            sys.exit(0)
        elif op in ('-h', '--help'):
            print(usage)
            sys.exit(0)

    cli = P3D_HostCLI()
    #cli.parse_cmdline(sys.argv[1:]) # util si se invoca con carga de archivo de comandos
    try:
        cli.cmdloop('Iniciando entrada de órdenes...')
    except SystemExit:
        msg = '\n' + '*' * 33
        msg = msg + '\nGracias por usar esta aplicación!'
        msg = msg + '\n' + '*' * 33 + '\n'
        print(msg)
    except:
        cli.do_motores('no')
        cli.do_desconectar_robot()
        logging.error(_("Excepción no controlada:") + "\n" + traceback.format_exc())
    finally:
        msg = 'Interprete de Línea de Comandos finalizado\n'
        print(msg)





