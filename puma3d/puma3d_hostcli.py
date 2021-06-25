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

from cmd import Cmd
import serial
import time
import logging
import traceback
import os
from colorama import Cursor, init, Fore, Style
from puma3d.puma3d_rpc import Puma3DRPC
from puma3d.puma3d_config import P3D_Config

class P3D_HostCLI(Cmd):
    """Interprete de Comandos para Control de RobotArm"""
    doc_header = "Ayuda de comandos documentados"
    undoc_header = "Ayuda de comandos no documentados"
    prompt = 'P3D$ '
    ruler = "*"       

    def __init__(self):
        Cmd.__init__(self)
        # Instancia de Serial conectada al robot. None cuando desconectado  
        self.connect = None
        self.port = P3D_Config.serial_port
        self.bauds = P3D_Config.serial_bauds
        # El robot está Desconectado: al comenzar
        #   Conectado: El robot ha respondido al comando de conexion
        #   Preparado: se ha ubicado en la posicion inicial con motores encendidos
        #   Trabajando:  El robot está ejecunado una secuencia
        # Preparado cuando: 
        self.robot_state = 'Desconectado'
        # El robot se encuentra trabajando con movimiento relativo | absoluto
        self.mov_mode = ''
        #ultima posicion registrada
        self.coords = None
        # Instancia de Puma3DRPC vinculada al Host. None cuando detenido
        self.rpc_server = None
        self.rpc_server_ip = P3D_Config.rpc_ip
        self.rpc_server_port = P3D_Config.rpc_port
        self.motors_enabled = False 
        self.camera_enabled = False 
        # Tiempo para actualizar imagenes de la camara
        self.refresh = 1000
        # Segundos de espera antes de empezar a ejecutar una instruccion de una secuencia
        self.delay = 0
        # Consignas para el robot
        # En este CLI Host corresponde archivo .p3ds (1 robot)
        # En red usando API REST, es archivo .p3dc (* robots)
        self.seq_file = None
        self.seq_dir = 'sequences'
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sequence = []
        self.seq_line = 0
        # Estados de una Tarea
        self.job_state = 'Nueva' # Nueva | Cargada | En_proceso | Pausada | Terminada
        # El robot se encuentra trabajando en modo manual | auto
        self.job_mode = 'manual'
        # Mensaje a mostrar en el punto de entrada de ordenes
        self.prompt_msg = ''
        # El robot está ejecutando una instrucción, true si ejecutando, false si pausado
        #self.moving = False

        init(autoreset=True)
        logging.basicConfig(filename=self.base_dir + '/puma3dhost.log', format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.DEBUG)
        logging.info('*' * 42 + '\nInterprete de Línea de Comandos: INICIADO')

    def preloop(self):
        f1 = Style.BRIGHT + Fore.GREEN
        f2 = Style.BRIGHT + Fore.BLUE
        f3 = Fore.WHITE
        f4 = Style.NORMAL
        msg = '\n' * 20 + f1 + '*' * 42
        msg = msg + '\n' + f2 + 'Bienvenido a la consola de control Puma3D!'
        msg = msg + '\n' + f1 + '*' * 42
        msg = msg + f4 + '\nEscriba \"help\" para listar los comandos disponibles.'
        print(msg)
        Cmd.preloop(self)

    def postloop(self):
        logging.info('Interprete de Línea de Comandos: FINALIZADO')
        Cmd.postloop(self)

    def default(self, args):
        print("Error. El comando \'" + args + "\' no esta disponible")

    def emptyline(self):
        """Usado cuando se ingresa una linea vacía (no quitar)"""
        self.prompt_msg = ''
        pass

    def precmd(self, args):
        self.prompt_msg = ''
        if self.job_state == 'Trabajando' and self.delay > 0:
            time.sleep(self.delay)
        if args != '':
            parts = args.split()
            parts[0] = parts[0].lower()
            args = ' '.join(parts)
        return(args)        

    def promptf(self):
        """Funcion para actualizar el prompt."""
        # if self.rpc_server == None:
        #     sprompt = 'S: No, '
        # else:
        #     sprompt = 'S: Sí, '
        # sprompt = sprompt + 'M: ' + ('Sí' if self.motors_enabled else 'No') + ', '
        # sprompt = sprompt +  'R: ' + self.robot_state + ', ' + 'T: ' + self.job_state + ', '
        # if self.job_state in ['Cargada', 'En_proceso']:
        #     sprompt = sprompt + 'A: '  + self.seq_file + ', '
        # if self.prompt_msg != '':
        #     sprompt = sprompt + 'RO: ' + self.prompt_msg + '\n\n'
        # else:
        #     sprompt = sprompt + '\n\n'
        # sprompt = sprompt + 'P3D$ '
        # return sprompt

        f1 = Style.BRIGHT + Fore.GREEN
        f2 = Style.BRIGHT + Fore.BLUE
        f3 = Fore.WHITE
        f4 = Style.NORMAL
        f5 = Style.NORMAL + Fore.GREEN
        sprompt = '\n' + f2 + 'S:' + f3
        if self.rpc_server == None:
            sprompt =sprompt + ' No, '
        else:
            sprompt =sprompt + ' Sí, '
        sprompt = sprompt +  f2 + 'M: ' +  f3 + ('Sí' if self.motors_enabled else 'No') + ', '
        sprompt = sprompt +  f2 + 'R: ' +  f3 + self.robot_state + ', ' + f2 + 'T: ' + f3 + self.job_state + ', '
        if self.job_state in ['Cargada', 'En_proceso']:
            sprompt = sprompt +  f2 + 'A: '  +  f3 + self.seq_file + ', '
        if self.prompt_msg != '':
            sprompt = sprompt +  f2 + 'RO: '  +  f5 + self.prompt_msg + '\n\n'
        else:
            sprompt = sprompt + '\n\n'
        sprompt = sprompt + f4 + f3 + 'P3D$ '
        return sprompt

    def postcmd(self, stop, line):
        """Funcion para actualizar el prompt despues de ejecuta cada comando."""
        self.prompt = self.promptf()

    def respuesta(self):
        sino = input("s/n: ").lower()
        if sino not in ['s', 'si', 'n', 'no']:
            return self.respuesta()
        elif sino in ['s', 'si']:
            return True
        return False

    def parser_out20sffactory(self, auxpos):
        # la posicion viene dada en el formato
        # "mensaje [X:123.00 Y:123.00 Z:123.00 E:123.00]"
        #logging.debug("Entrada: " + auxpos)
        if auxpos == '':
            return False
        auxpos = auxpos.rstrip()
        ix = auxpos.find('[')
        if ix < 0:
            return False
        else:
            try:
                coords = auxpos[ix+1:len(auxpos)-1]
                coords = coords.split(' ')
                #logging.debug("Intermedio: " + str(coords))
                if len(coords) != 4:
                    raise
                else:
                    x = str(coords[0])[2:len(str(coords[0]))]
                    xf = float(x)
                    y = str(coords[1])[2:len(str(coords[1]))]
                    yf = float(y)
                    z = str(coords[2])[2:len(str(coords[2]))]
                    zf = float(z)
                    e = str(coords[3])[2:len(str(coords[2]))-2]
                    ef = float(e)
                    self.coords = { 'X': xf,  'Y': yf, 'Z': zf, 'E': ef }
                    pos = 'X' + x + ' ' + 'Y' + y + ' ' +'Z' + z + ' ' +'E' + e
                    return pos
            except Exception:
                logging.debug("Parser: " + str(coords) + '\n' + traceback.format_exc())
                return False
                
    def parser_outmarlin(self):
        pass

    def parser_filecheck(self, filepath):
        chk = True
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip('\n')
                    if line == '':
                        continue
                    if line[0] == ';':
                        continue
                    if ';' in line:
                        line = line.split(';')[0]
                    parts = line.split(' ')
                    if len(parts) == 0:
                        continue
                    token = parts[0]
                    if token not in ['G0', 'G1', 'G4', 'G28', 'G90', 'G91', 'G92',
                                'M1', 'M2', 'M3', 'M5', 'M6', 'M7', 'M17', 'M18', 
                                'M106', 'M107', 'M114', 'M119']:
                        raise Exception('Comando ' + token + ' no admitido')
                    if token == 'G4' and len(parts) != 2:
                        raise Exception('Comando G4 incorrecto')
                    if token in ['G0', 'G1', 'G92'] and len(parts) < 2:
                        raise Exception('Comando ' + token + ' incorrecto')
                    self.sequence.append(line+'\r')
                f.close()
        except:
            chk = False
        return chk

    def do_salir(self, args):
        """salir: sale del interprete"""
        msg = 'Orden salir ' + args + '.'
        if self.robot_state == 'Trabajando' and args != "forzado":
            print('Está seguro de terminar mientras está en ejecución? (esto abortará la secuencia).')
            if not self.respuesta():
                return
        try:
            if self.rpc_server is not None:
                misocket = self.rpc_server.socket
                self.rpc_server.shutdown()
                self.rpc_server = None
                misocket.close()
                self.do_motores('no')
                self.do_desconectar()
        except:
            msg = msg + '\n' + traceback.format_exc()
            logging.error(msg)
        else:
            logging.debug(msg)
            time.sleep(1)
        raise SystemExit

    def do_conectar(self, args=''):
        """conectar: Conecta al host con el robot usando un puerto y velocidad [en bps] dados
        \rValores por defecto: /dev/ttyACM0 y 115200
        \rSintaxis: conectar [puerto baudios]"""
        msg = 'Orden conectar ' + args + ': '
        if self.robot_state == 'Desconectado':
            timeout = None
            if args == '' or len(args.split()) <= 1:
                port = self.port
                bauds =self.bauds
            else:
                params = args.split()
                port = str(params[0]) 
                bauds = params[1]
            try:
                self.connect = serial.Serial(port, bauds, timeout=timeout)
                time.sleep(2)
                self.port = port
                self.bauds = bauds
                self.robot_state = 'Conectado'                 
                self.mov_mode = 'absoluto'
                self.prompt_msg = 'Conectado en ' + port + ' a ' + str(bauds)
                msg = msg + self.prompt_msg
                logging.info(msg)
            except Exception:
                self.robot_state = 'Desconectado'
                self.motors_enabled = False
                self.prompt_msg = 'Robot no vinculado. Verifique instalación o reinicie.'
                msg = msg + 'No es posible conectar al robot en ' + port + ' a ' + str(bauds)
                msg = msg + '\n' + traceback.format_exc()
                logging.error(msg)
        else:
            msg = msg + "Sin cambios"
            logging.debug(msg)

    def do_desconectar(self, args):
        """desconectar: libera la conexion del host al robot"""
        msg = 'Orden desconectar '+ args + ': '
        if self.robot_state != 'Desconectado':
            try:
                # self.connect.write(b'M18\r') # analizar conveniencia
                self.connect.close()
                msg = msg + 'Robot desconectado.'
                logging.debug(msg)
            except:
                msg = msg + '\n' + traceback.format_exc()
                logging.error(msg)
        self.connect = None
        self.robot_state = 'Desconectado'

    def ddo_gcode(self, args=''):  
        """gcode: Ejecuta una orden bajo sintaxis g-code.
        \rSintaxis: gcode Codigo_de_Orden [Argumento]"""
        msg = 'Orden gcode '+ args + ': '
        if args == '':
            self.prompt_msg = 'Argumentos incorrectos.'
            msg = msg + self.prompt_msg
            logging.error(msg)
            self.onecmd('help gcode')
            return
        return
        if self.connect is not None:
            if  self.motors_enabled:
                if self.robot_state == 'Preparado':
                    gc = x = y = z = speed = None
                    values = args.split(' ')
                    count = len(values)
                    if count > 3 and values[0] in ['a', 'r']:
                        mode = 'absoluto' if values[0] == 'a' else 'relativo'
                        if mode != self.mov_mode:
                            self.do_modo(mode)
                        self.connect.reset_input_buffer()
                        if mode == self.mov_mode:
                            try:
                                x = float(values[1])
                                y = float(values[2])
                                z = float(values[3])
                                gc = ' X' + str(x) + ' Y' + str(y) + ' Z' + str(z)
                                if count == 5:
                                    speed = float(values[4])
                                    gc = 'G1' + gc + ' F'+ str(speed) + '\r'
                                else:
                                    gc = 'G1' + gc + '\r'
                                self.connect.write(bytearray(gc, 'utf-8'))
                                resp = 'OTHER'
                                while True:
                                    ret = self.connect.readline()
                                    reta = ret.decode("utf-8")
                                    #logging.debug('retorno MOVE:' + reta)
                                    if 'MOVE' in reta :
                                        resp = reta #[0:len(reta)-1] 
                                    elif 'FAILURE' in reta:
                                        resp = 'FAILURE'
                                    if "ok" in reta:
                                        break
                                if resp != 'FAILURE':
                                    pos = self.parser_out20sffactory(resp)
                                    #logging.debug("Retorna Mensaje: " + str(pos))
                                    if pos != False:
                                        self.prompt_msg = 'P(' + pos + ')'
                                    else:
                                        self.prompt_msg = 'Revise, posicion informada con error.'
                                    self.robot_state = "Preparado"
                                    self.motors_enabled = True
                                    msg = msg + self.prompt_msg
                                    logging.info(msg)
                                else:
                                    self.robot_state = 'Fuera de servicio' # Conectado
                                    self.do_motores('no')
                                    self.coords = None
                                    self.prompt_msg = 'Robot dañado o falta energía.'
                                    msg = msg + self.prompt_msg
                                    logging.error(msg)
                            except ValueError:
                                self.prompt_msg = 'Argumentos incorrectos.'
                                msg = msg + self.prompt_msg
                                logging.error(msg)
                                self.onecmd('help cartes')
                            except:
                                self.prompt_msg = 'Error interno.'
                                msg = msg + self.prompt_msg + '\n\tConsigna: ' + args 
                                trace = msg + '\n' + traceback.format_exc()
                                logging.error(trace)
                        else:
                            self.prompt_msg = 'No puedo cambiarse el modo a ' + mode + '.'
                            msg = msg + self.prompt_msg
                            logging.error(msg)
                    else:
                        self.prompt_msg = 'Argumentos ' + args +' incorrectos.'
                        msg = msg + self.prompt_msg
                        logging.error(msg)
                        self.onecmd('help cartes')
                else:
                    self.prompt_msg = 'El Robot debe estar preparado (post homing).'
                    msg = msg + self.prompt_msg
                    logging.error(msg)
            else:
                self.prompt_msg = 'Los motores deben estar encendidos.'
                msg = msg + self.prompt_msg
                logging.error(msg)
        else:
            self.prompt_msg = 'No hay conexión con el Robot.'
            msg = msg + self.prompt_msg
            logging.error(msg)


    def do_servidor(self, args):   # value=si|no
        """ servidor: Inicia/detiene el servidor RPC del Host
        \rSintaxis: servidor si|no"""
        msg = 'Orden servidor ' + args + ': '
        args = args.lower()
        if args != '' and args in ['si','no']:
            logging.debug(msg + 'Iniciando solicitud ...')
            try:
                if args == 'si':
                    if self.rpc_server is None:
                        self.rpc_server = Puma3DRPC(self)
                        msg = msg + 'Encendido.'
                else:
                    if self.rpc_server is not None:
                        misocket = self.rpc_server.socket
                        self.rpc_server.shutdown()
                        self.rpc_server = None
                        misocket.close()
                        msg = msg + 'Apagado.'
                logging.info(msg)
            except:
                msg = msg + '\n' + traceback.format_exc()
                logging.error(msg)
        else:
            self.prompt_msg = 'Argumento incorrecto.'
            msg = msg + self.prompt_msg
            logging.error(msg)
            self.onecmd('help servidor')

    def do_motores(self, args):  # 1 si, 2 no
        """motores: Enciende/Apaga (activa/desactiva) los motores del robot
        \rSintaxis: motores si|no"""
        # mejora: analizar funcion que ajuste el estado cuando falle un write
        msg = 'Orden motores ' + args + ': '
        if self.robot_state in ['Conectado', 'Preparado', 'Trabajando']:
            if args != '' and args.lower() in ['si','no']:
                try:
                    if args.lower() == 'si':
                        self.connect.write(b'M17\r')
                        self.motors_enabled = True
                        self.prompt_msg = 'Motores encendidos.'
                    else:
                        self.connect.write(b'M18\r')
                        self.motors_enabled = False
                        self.robot_state = 'Conectado'
                        self.prompt_msg = 'Motores apagados, calibración perdida.'
                    msg = msg + self.prompt_msg
                    logging.debug(msg)
                except:
                    self.prompt_msg = 'No hay conexión con el Robot.'
                    msg = msg + self.prompt_msg
                    logging.error(msg)
            else:
                self.prompt_msg = 'Argumento incorrecto'
                msg = msg + self.prompt_msg
                logging.error(msg)
                self.onecmd('help motores')
        else:
            self.prompt_msg = 'No hay conexión con el Robot.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def do_cargar(self, args):
        """cargar: lee un archivo de tarea para el robot conectado"""
        msg = 'Orden cargar '+ args + ': '
        if self.robot_state != 'Trabajando':
            base_dir = self.base_dir + '/' + self.seq_dir + '/'
            if os.path.exists(base_dir):
                if args == '':
                    content = os.listdir(base_dir)
                    names = []
                    for file in content:
                        if os.path.isfile(os.path.join(base_dir, file)) and file.endswith('.p3ds'):
                            names.append(file)
                    print('Archivos disponibles:\n' + str(names))                
                    filename = input("Archivo elegido [.p3ds ]?: ").lower()
                else:
                    filename = args
                    
                if os.path.exists(base_dir + filename):
                    if self.parser_filecheck(base_dir + filename):
                        self.seq_file = filename
                        self.job_state = 'Cargada'
                        self.prompt_msg = str(len(self.sequence)) + ' comandos.'
                        msg = msg + self.prompt_msg
                        logging.debug(msg)
                    else:
                        self.seq_file = None
                        self.job_state = 'Nueva'
                        self.prompt_msg = 'Archivo ' + filename + ' con error de formato o lectura.'
                        msg = msg + self.prompt_msg  + '\n' + traceback.format_exc()
                        logging.error(msg)
                else:
                    self.seq_file = None
                    self.job_state = 'Nueva'
                    self.prompt_msg = 'El archivo no existe.'
                    msg = msg + self.prompt_msg
                    logging.error(msg)
            else:
                self.seq_file = None
                self.job_state = 'Nueva'
                self.prompt_msg = 'Falta el directorio con las secuencias de trabajo.'
                msg = msg + self.prompt_msg
                logging.error(msg)
        else:
            self.prompt_msg = 'No corresponde, hay una tarea en proceso.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def do_procesar(self, args):  # 3
        """procesar: Inicia una secuencia de consignas de trabajo (tarea de un robot)"""
        msg0 = 'Orden procesar ' + args + ': '
        if  self.connect is None:
            msg = '* Requiere de conexión al Robot.'
            logging.warning(msg)
            self.do_conectar()
        if  self.connect is not None and not self.motors_enabled:
            msg = '* Requiere motores encendidos.'
            logging.warning(msg)
            self.do_motores('si')
        if  self.connect is not None and self.motors_enabled and self.robot_state != 'Preparado':
            msg = '* Requiere que el Robot se ubique en el punto inicio.'
            logging.warning(msg)
            self.do_inicio('')
        if self.connect is not None and self.motors_enabled and self.robot_state == 'Preparado' and (self.job_state in ['Cargada',  'Terminada']):
            self.robot_state = "Trabajando"
            self.job_state == 'En_proceso'
            self.seq_line = 0
            # Inicia la ejecución de la secuencia cargada
            try:
                # if 'G28' in self.sequence[0]: # self.onecmd('inicio')
                #     self.seq_line = self.seq_line + 1
                for cmd in self.sequence:
                    self.connect.write(bytearray(cmd, 'utf-8'))
                    subs = ''
                    while True:
                        resp = self.connect.readline()
                        if "ok" in resp.decode("utf-8"):
                            break
                    msg = 'GCode: ' + cmd
                    logging.info(msg)

                self.robot_state = 'Preparado'
                self.prompt_msg = 'Secuencia finalizada con éxito.'
            except:
                msg = msg0 + 'Se ha producido un error'
                msg = msg + traceback.format_exc()
                logging.error(msg)
                self.prompt_msg = "Error: estados indeterminados. Reinicie."
                self.do_motores('no')
            msg = msg0 + self.prompt_msg
            logging.info(msg)
        else:
            self.prompt_msg = 'Robot desconectado o falta la Tarea.'
            msg = msg0 + self.prompt_msg
            logging.error(msg)

    def ddo_pausar(self, args):  # 4
        """pausar: Suspende la secuencia de la tarea en ejecución"""
        msg = 'Orden pausar '+ args + ': '
        if self.job_state == 'En_proceso':
            self.job_state = 'Pausada'
            msg = msg + 'Listo.'
            logging.debug(msg)
        else:
            self.prompt_msg = 'No hay tarea que suspender.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def ddo_continuar(self, args):  # 5
        """continuar: Continua la ejecución de la secuencia Pausada"""
        msg = 'Orden continuar '+ args + ': '
        if self.job_state == 'Pausada':
            self.job_state = 'En_proceso'
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            self.prompt_msg = 'No hay tarea en suspenso.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def ddo_detener(self, args):  # 6
        """detener: Detiene (aborta) la secuencia de la tarea en ejecución"""
        msg = 'Orden detener '+ args + ': '
        if self.job_state == 'En_proceso' or self.job_state == 'Pausada':
            self.job_state = 'Terminada'
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            self.prompt_msg = 'No hay tarea que detener.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def reiniciar(self, args):  # 7
        """reiniciar: Reinicia el sistema al estado inicial.
        \rLimpia la tarea Cargada y libera los robots, donde el robot seleccionado trabaja"""
        msg = 'Orden reiniciar '+ args + ': '
        if self.robot_state != 'Desconectado':
            self.do_desconectar('')
            self.robot_state = 'Desconectado'
            self.job_state = 'Nueva'
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            self.prompt_msg = 'El Sistema se ha reiniciado.'
            msg = msg +  + self.prompt_msg
            logging.info(msg)
        
    def set_gripper_step(self, args):  # 10
        """quit: Configurar el avance lineal de apertura/cierre de pinza	Valor de desplazamiento (en mm)"""
        msg = 'Orden gripper_step '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_gripper_speed(self, args):  # 11
        """gripper_speed: Configurar la velocidad de apertura/cierre de pinza. Valor de velocidad (en mm/min)"""
        msg = 'Orden gripper_speed '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_gripper_min(self, args):  # 12
        """gripper_min: Configurar la apertura mínima de la pinza	Valor (en mm)"""
        msg = 'Orden gripper_min '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_gripper_press(self, args):  # 13
        """gripper_press: Configurar la presion mínima de la pinza	Valor (en g/mm2)"""
        msg = 'Orden gripper_press '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_angular_speed(self, args):  # 15
        """angular_speed: Configurar la velocidad de rotación de la articulación. Valor de velocidad (en grado sex./min). Identificador de la articulación (B|L|H). Las opciones responden a las características del robot usado (RRR, en este caso)"""
        msg = 'Orden angular_speed '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_angular_step(self, args):  # 16
        """angular_step: Configurar el desplazamiento angular	Valor del angulo (en grado sex.)"""
        msg = 'Orden angular_step '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_linear_speed(self, args):  # 17
        """linear_speed: Configurar la velocidad de desplazamiento lineal en el extremo (efector final). Valor de velocidad (en mm/min)"""
        msg = 'Orden linear_speed '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def set_lineal_step(self, args):  # 18
        """lineal_step: Configurar el desplazamiento lineal en el extremo (efector final). Valor de desplazamiento (en mm)"""
        msg = 'Orden lineal_step '+ args + ': '
        if self.online:
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def ddo_fin_carrera(self, args):  # 20
        """origen_angular B|L|H
        \rMueve al punto de fin de carrera la articulación indicada (Base | Lower | Higher)"""
        msg = 'Orden fin_carrera '+ args + ': '
        if self.robot_state == 'Conectado' or self.robot_state == 'Preparado':
            msg = msg  + ': Final de carrera alcanzado.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def ddo_angular(self, args):  # 21
        """angular B|L|H angulo velocidad
        \rMueve la articulación con desplazamiento rotacional relativo
        \run ángulo [en º sex. con signo] a la velocidad dada [mm/min]. 
        \rIdentificador de la articulación (Base|Lower|Higher). 
        \rLas opciones responden a las características del robot usado (RRR, en este caso)"""
        msg = 'Orden angular '+ args + ': '
        if self.robot_state == 'Preparado':
            msg = msg + 'Listo.'
            logging.info(msg)
        else:
            msg = msg + 'Robot desconectado.'
            logging.error(msg)
        
    def do_inicio(self, args):  # 22
        """inicio: Mueve el extremo (efector final) a su posición XYZ inicial, por defecto [0, 175, 120]"""
        msg = 'Orden inicio: '
        if self.robot_state == 'Trabajando':
            self.prompt_msg = 'Robot ocupado en otra tarea.'
            msg = msg + self.prompt_msg
            logging.error(msg)
        elif self.robot_state in ['Conectado', 'Preparado']:
            self.connect.reset_input_buffer()
            self.connect.write(b'G28\r')
            time.sleep(6)
            resp = 'OTHER'
            while True:
                ret = self.connect.readline()
                reta = ret.decode("utf-8")
                #logging.debug('reta:' + reta)
                if 'COMPLETE' in reta :
                    resp = 'COMPLETE' 
                elif 'FAILURE' in reta:
                    resp = 'FAILURE'
                if "ok" in reta:
                    break
            if resp != 'FAILURE':
                self.connect.write(b'M114\r')
                auxpos = ''
                while True:
                    ret = self.connect.readline()
                    reta = ret.decode("utf-8")
                    #logging.debug("retorno 114: " + reta)
                    if "CURRENT" in reta:
                        auxpos = reta 
                    if "ok" in reta:
                        break
                pos = self.parser_out20sffactory(auxpos)
                #logging.debug("Retorna Mensaje: " + str(pos))
                if pos != False:
                    self.prompt_msg = 'P(' + pos + ')'
                else:
                    self.prompt_msg = 'Revise, posicion informada con error.'
                self.robot_state = "Preparado"
                self.motors_enabled = True
                self.mov_mode = 'absolute'
                msg = msg + self.prompt_msg
                logging.debug(msg)
            else:
                self.robot_state = 'Fuera de Servicio'
                self.motors_enabled = False
                self.mov_mode = ''
                self.coords = None
                self.prompt_msg = 'Robot dañado o falta energía.'
                msg = msg + self.prompt_msg
                logging.error(msg)
            # elif resp == '???':
            #     self.robot_state = "Conectado"
            #     self.prompt_msg = 'futuro evento alternativo.'
            #     msg = msg + ': ' + self.prompt_msg
            #     logging.error(msg)
        elif self.robot_state == "Desconectado":
            self.motors_enabled = False
            self.mov_mode = ''
            self.prompt_msg = 'No hay conexión con el Robot.'
            msg = msg + self.prompt_msg
            logging.error(msg)
        else:
            # Fuera de servicio
            self.robot_state = 'Fuera de Servicio'
            self.motors_enabled = False
            self.mov_mode = ''
            self.coords = None
            self.prompt_msg = 'Robot dañado o falta energía.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def do_cartes(self, args=''):  # 23: r=relativo,  24: a=absoluto
        """cartes: Mueve el extremo del robot (efector final) las distancias x, y, z indicadas  
        \r[en mm] si es movimiento relativo [r], a partir de su posición actual y a la velocidad dada
        \r[en mm/min], o a las coordenadas correspondientes, si el movimiento es absoluto [a].
        \rSintaxis: cartes [a|r] x y z [velocidad]"""
        msg = 'Orden cartes '+ args + ': '
        if args == '':
            self.prompt_msg = 'Argumentos incorrectos.'
            msg = msg + self.prompt_msg
            logging.error(msg)
            self.onecmd('help cartes')
            return

        if self.connect is not None:
            if  self.motors_enabled:
                if self.robot_state == 'Preparado':
                    gc = x = y = z = speed = None
                    values = args.split(' ')
                    count = len(values)
                    if count > 3 and values[0] in ['a', 'r']:
                        mode = 'absoluto' if values[0] == 'a' else 'relativo'
                        if mode != self.mov_mode:
                            self.do_modo(mode)
                        self.connect.reset_input_buffer()
                        if mode == self.mov_mode:
                            try:
                                x = float(values[1])
                                y = float(values[2])
                                z = float(values[3])
                                gc = ' X' + str(x) + ' Y' + str(y) + ' Z' + str(z)
                                if count == 5:
                                    speed = float(values[4])
                                    gc = 'G1' + gc + ' F'+ str(speed) + '\r'
                                else:
                                    gc = 'G1' + gc + '\r'
                                self.connect.write(bytearray(gc, 'utf-8'))
                                resp = 'OTHER'
                                while True:
                                    ret = self.connect.readline()
                                    reta = ret.decode("utf-8")
                                    #logging.debug('retorno MOVE:' + reta)
                                    if 'MOVE' in reta :
                                        resp = reta #[0:len(reta)-1] 
                                    elif 'FAILURE' in reta:
                                        resp = 'FAILURE'
                                    if "ok" in reta:
                                        break
                                if resp != 'FAILURE':
                                    pos = self.parser_out20sffactory(resp)
                                    #logging.debug("Retorna Mensaje: " + str(pos))
                                    if pos != False:
                                        self.prompt_msg = 'P(' + pos + ')'
                                    else:
                                        self.prompt_msg = 'Revise, posicion informada con error.'
                                    self.robot_state = "Preparado"
                                    self.motors_enabled = True
                                    msg = msg + self.prompt_msg
                                    logging.info(msg)
                                else:
                                    self.robot_state = 'Fuera de servicio' # Conectado
                                    self.do_motores('no')
                                    self.coords = None
                                    self.prompt_msg = 'Robot dañado o falta energía.'
                                    msg = msg + self.prompt_msg
                                    logging.error(msg)
                            except ValueError:
                                self.prompt_msg = 'Argumentos incorrectos.'
                                msg = msg + self.prompt_msg
                                logging.error(msg)
                                self.onecmd('help cartes')
                            except:
                                self.prompt_msg = 'Error interno.'
                                msg = msg + self.prompt_msg + '\n\tConsigna: ' + args 
                                trace = msg + '\n' + traceback.format_exc()
                                logging.error(trace)
                        else:
                            self.prompt_msg = 'No puedo cambiarse el modo a ' + mode + '.'
                            msg = msg + self.prompt_msg
                            logging.error(msg)
                    else:
                        self.prompt_msg = 'Argumentos ' + args +' incorrectos.'
                        msg = msg + self.prompt_msg
                        logging.error(msg)
                        self.onecmd('help cartes')
                else:
                    self.prompt_msg = 'El Robot debe estar preparado (post homing).'
                    msg = msg + self.prompt_msg
                    logging.error(msg)
            else:
                self.prompt_msg = 'Los motores deben estar encendidos.'
                msg = msg + self.prompt_msg
                logging.error(msg)
        else:
            self.prompt_msg = 'No hay conexión con el Robot.'
            msg = msg + self.prompt_msg
            logging.error(msg)

    def ddo_mpinza(self, args):  # 25
        """mpinza magnitud velocidad
        \rMueve el efector final según la magnitud y velocidad dadas"""
        msg = 'Orden mpinza '+ args + ': '
        logging.info(msg)
        
    def detener_pinza(self, args):  # 26
        """detener_pinza
        \rDetiene el efector final"""
        msg = 'Orden detener_pinza '+ args + ': '
        logging.info(msg)
        
    def verifica_conexion(self, args=''):  # 40
        """verifica_conexion
        \rRealiza una prueba de conectividad con el robot. Con argumento si: intenta reconectar"""
        msg = 'Orden verifica_conexion '+ args + ': '
        if self.robot_state == 'Desconectado':
            if args == 'si':
                self.do_conectar('')

        if self.robot_state in ['Conectado', 'Preparado', 'Trabajando']:
            # prueba recuperacion de datos
            try:        
                self.connect.write(b'M114\r')
                auxpos = ''
                while True:
                    ret = self.connect.readline()
                    reta = ret.decode("utf-8")
                    if "CURRENT" in reta:
                        auxpos = reta 
                    if "ok" in reta:
                        break
                pos = self.parser_out20sffactory(auxpos)
                if pos != False:
                    self.prompt_msg = 'P(' + pos + ')'
                else:
                    self.prompt_msg = 'posición informada con errores'
                msg = msg + self.robot_state
                logging.debug(msg)
            except:
                self.robot_state = 'Desconectado'
                self.prompt_msg = 'Robot no vinculado. Verifique o reinicie la instalación.'
                logging.error(msg)

            # agregar prueba de movimiento (detección de fallo electrico)
        else:
            msg = msg + self.robot_state
            logging.debug(msg)

    def get_estado_sensor(self, args):  # 41
        """estado_sensor: Recupera el estado del sensor auxiliar especificado por su id
        \rSintaxis: estado_sensor id"""
        msg = 'Orden estado_sensor '+ args + ': '
        logging.info(msg)
        
    def ddo_camara(self, args):  # 42 si, 43 no
        """camara: Conectar/Desconectar el servidor de stream (video). Valor por defecto: No
        \rSintaxis: camara si|no"""
        msg = 'Orden camara '+ args + ': '
        if args != '' and args.lower() in ['si','no']:
            self.camera_enabled = True if args == 'si' else False
            msg = msg + 'Listo. cam: ' + str(self.camera_enabled)
            logging.info(msg)
            
    def ddo_fijar_retardo(self, args):  # 50
        """fijar_retardo: configura el tiempo de espera antes de ejecutar la próxima instrucción. Valor [en s]
        \rSintaxis: fijar_retardo valor"""
        msg = 'Orden fijar_retardo '+ args + ': '
        try:
            self.delay = int(args)            
            msg = msg + 'Listo.'
            logging.info(msg)
        except ValueError:
            msg = msg + 'Argumentos incorrectos (' + args +')'
            logging.error(msg)
            self.onecmd('help fijar_retardo')

    def do_modo(self, args=''):  # 51: manual, 52: auto, 90: absoluto, 91: relativo
        """modo: Selecciona el modo de trabajo para el robot actual.
        \rSintaxis: modo [manual|auto|absoluto|relativo]"""
        # Modos manual y auto no producen efectos en la API para proxima version almacenar estado de trabajo del usuario en BD
        msg = 'Orden fijar_modo '+ args + ': '
        args = args.lower()
        if args == '' or args not in ['manual', 'auto', 'absoluto', 'relativo']:
            msg = 'Argumento "' + str(args) + '" inválido'
            logging.error(msg)
            self.onecmd('help modo')
            return
        if self.robot_state == 'Trabajando':
            self.prompt_msg = 'No puede cambiarse modo durante la ejecución de secuencias.'
            msg = msg + self.prompt_msg
            logging.error(msg)
        elif self.robot_state == 'Desconectado':
            self.prompt_msg = 'El Robot se encuentra desconectado.'
            msg = msg + self.prompt_msg
            logging.error(msg)
        elif self.robot_state in ['Conectado', 'Preparado']:
            if args == 'manual':
                self.job_mode = 'manual'
                self.prompt_msg = 'Modo cambiado'
                msg = msg + self.prompt_msg
                logging.debug(msg)
            elif args == 'auto':
                self.job_mode = 'auto'
                self.prompt_msg = 'Modo cambiado'
                msg = msg + self.prompt_msg
                logging.debug(msg)
            elif args == 'relativo':
                try:
                    self.connect.write(b'G91\r')
                    while True:
                        ret = self.connect.readline()
                        reta = ret.decode("utf-8")
                        if "ok" in reta:
                            break
                    self.mov_mode = 'relativo'
                    self.prompt_msg = 'Modo cambiado'
                    msg = msg + self.prompt_msg
                    logging.debug(msg)
                except:
                    self.prompt_msg = 'El modo no ha cambiado'
                    msg = msg + self.prompt_msg + '\n' + traceback.format_exc()
                    logging.error(msg)
            else:
                # args == 'absoluto':
                try:
                    self.connect.write(b'G90\r')
                    while True:
                        ret = self.connect.readline()
                        reta = ret.decode("utf-8")
                        if "ok" in reta:
                            break
                    self.mov_mode = 'absoluto'
                    self.prompt_msg = 'Modo cambiado'
                    msg = msg + self.prompt_msg
                    logging.debug(msg)
                except:
                    self.prompt_msg = 'El modo no ha cambiado'
                    msg = msg + self.prompt_msg + '\n' + traceback.format_exc()
                    logging.error(msg)
         
    def ddo_fijar_refresco(self, args):  # 53
        """fijar_refresco valor: Configurar tiempo de actualización de datos del servidor de stream. Valor del intervalo (en ms)"""
        msg = 'Orden fijar_refresco '+ args + ': '
        try:
            self.refresh = int(args)            
            msg = msg + 'Listo.'
            logging.info(msg)
        except ValueError:
            msg = msg + 'Argumentos incorrectos (' + args +')'
            logging.error(msg)
            self.onecmd('help fijar_refresco')

    def do_prueba(self, args):
        """prueba: Conecta con el robot, realiza un homing, ejecuta una secuencia de prueba
        \ncon movimientos relativos y absolutos, se desactivan los motores del robot"""
        msg0 = 'Orden prueba '+ args + ': '
        if self.robot_state == 'Preparado':

            # Idea de cambio de estado
            # A usar en lazo de carga de comandos desde archivo o remoto
            self.robot_state = 'Trabajando' 
            msg = msg0 + ': INICIADA.'
            logging.info(msg)

            cmdList = ["M17",
                "G91",
                "G1 X10 Y20 Z10 F40",
                "G1 X0 Y20 Z0 F25",
                "G1 X10 Y0 Z-30 F40",
                "G1 X-20 Y-50 Z0 F30",
                "G1 X0 Y20 Z0 F40",
                "G1 X-45 Y40 Z30 F25",
                "G1 X0 Y0 Z-215 F35",
                "G1 X40 Y-30 Z0 F25",
                "G90",
                "G1 X0 Y175 Z120 F40",
                "G1 X-150 Y75 Z20 F30",
                "G1 X-150 Y150 Z20 F40",
                "G1 X0 Y175 Z0 F40",
                "G1 X120 Y120 Z-75 F30",
                "M114",
                ]
            try:
                self.onecmd('inicio')

                for aCmd in cmdList:
                    cmd_temp = aCmd + '\r'
                    self.connect.write(bytearray(cmd_temp, 'utf-8'))
                    while True:
                        a = self.connect.readline()
                        if "X" in a.decode("utf-8"):
                            subs = str(a)[2:(len(str(a))-5)]
                            msg = 'Orden GCode: ' + subs
                            logging.info(msg)
                        if "ok" in a.decode("utf-8"):
                            break
                self.robot_state = 'Preparado'
                self.prompt_msg = "Secuencia finalizada con éxito."
                msg = msg0 + ': FINALIZADA.'
                logging.info(msg)
            except:
                msg = msg0 + ': Se ha producido un error'
                msg = msg + traceback.format_exc()
                logging.error(msg)
                self.prompt_msg = "Error: estados indeterminados. Reinicie."
                self.do_motores('no')
        else:
            msg = msg0 + 'Robot ocupado o desconectado.'
            logging.error(msg)
