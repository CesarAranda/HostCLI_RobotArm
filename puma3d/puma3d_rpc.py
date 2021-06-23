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

from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
import socket
import traceback
import logging

# Los Host deben tener direccion IP y Port fijos, y
# coincidir con lo almacenado en la base de datos de la API.
RPC_PORT = 7994

class Puma3DRPC(object):

    def __init__(self, p3d):
        self.p3d = p3d
        self.host = p3d.rpc_server_ip
        self.port = p3d.rpc_server_port
        self.socket = None

        try:
            self.server = SimpleXMLRPCServer((self.host, self.port),
                                                 allow_none = True,
                                                 logRequests = False)
            if self.port != RPC_PORT:
                logging.warning('Servidor RPC escuchando en el puerto (no predeterminado) ' + str(self.port))
            logging.info('Servidor RPC (predeterminado) en ' + self.host + ':' + str(self.port))
            self.socket = self.server.socket
        except:
            logging.error('Servidor RPC no puede ejecutarse en ' + self.host + ':' + str(self.port))
            logging.error(traceback.format_exc())
            raise 

        self.server.register_function(self.motor_on, 'motor_on') # 1
        self.server.register_function(self.motor_off, 'motor_off') # 2
        self.server.register_function(self.job_start, 'job_start') # 3
        self.server.register_function(self.job_suspend, 'job_suspend') # 4
        self.server.register_function(self.job_resume, 'job_resume') # 5
        self.server.register_function(self.job_stop, 'job_stop') # 6
        self.server.register_function(self.reset, 'reset') # 7
        # self.server.register_function(self.set_gripper_step, 'set_gripper_step') # 10
        # self.server.register_function(self.set_gripper_speed, 'set_gripper_speed') # 11
        # self.server.register_function(self.set_gripper_min, 'set_gripper_min') # 12
        # self.server.register_function(self.set_gripper_press, 'set_gripper_press') # 13
        # self.server.register_function(self.set_angular_speed, 'set_angular_speed') # 15
        # self.server.register_function(self.set_angular_step, 'set_angular_step') # 16
        # self.server.register_function(self.set_linear_speed, 'set_linear_speed') # 17
        # self.server.register_function(self.set_lineal_step, 'set_lineal_step') # 18
        # self.server.register_function(self.endstop, 'endstop') # 20
        # self.server.register_function(self.move_angular_rel, 'move_angular_rel') # 21
        self.server.register_function(self.homing, 'homing') # 22
        self.server.register_function(self.move_cartes_rel, 'move_cartes_rel') # 23
        self.server.register_function(self.move_cartes_abs, 'move_cartes_abs') # 24
        # self.server.register_function(self.gripper_move, 'gripper_move') # 25
        # self.server.register_function(self.gripper_stop, 'gripper_stop') # 26
        self.server.register_function(self.comm_test, 'comm_test') # 40
        # self.server.register_function(self.sensor_state, 'sensor_state') # 41
        self.server.register_function(self.connect_camera, 'connect_camera') # 42
        self.server.register_function(self.disconnect_camera, 'disconnect_camera') # 43
        # self.server.register_function(self.delay, 'delay') # 50
        self.server.register_function(self.mode_manual, 'mode_manual') # 51
        self.server.register_function(self.mode_auto, 'mode_auto') # 52
        # self.server.register_function(self.set_time_refresh, 'set_time_refresh') # 53
        self.server.register_function(self.sequence_test, 'sequence_test')

        self.thread = Thread(target = self.run)
        self.thread.start()

    def run(self): 
        self.server.serve_forever()

    def shutdown(self): 
        self.server.shutdown()
        self.thread.join()

    # -------------------------------------------------
    def motor_on(self):  # 1
        self.p3d.do_motores('si')
        msg = 'motores("si")'
        logging.info('RPC: ' + msg)
        return {'robot_state': self.p3d.robot_state,
                'motors_enabled': self.p3d.motors_enabled
                }        

    def motor_off(self):  # 2
        self.p3d.do_motores('no')
        msg = 'motores("no")'
        logging.info('RPC: ' + msg)
        return {'robot_state': self.p3d.robot_state,
                'motors_enabled': self.p3d.motors_enabled
                }        

    def job_start(self):  # 3
        self.p3d.do_iniciar_tarea('')
        msg = 'procesar_tarea("")'
        logging.info('RPC: ' + msg)
        return {'job_state': self.p3d.job_state
                }        

    def job_suspend(self):  # 4
        self.p3d.do_pausar_tarea('')
        msg = 'pausar_tarea("")'
        logging.info('RPC: ' + msg)
        return {'job_state': self.p3d.job_state
                }        

    def job_resume(self):  # 5
        self.p3d.do_continuar_tarea('')
        msg = 'continuar_tarea("")'
        logging.info('RPC: ' + msg)
        return {'job_state': self.p3d.job_state
                }        

    def job_stop(self):  # 6
        self.p3d.do_detener_tarea('')
        msg = 'detener_tarea("")'
        logging.info('RPC: ' + msg)
        return {'job_state': self.p3d.job_state
                }        

    def reset(self):  # 7
        self.p3d.reiniciar('')
        msg = 'reiniciar("")'
        logging.info('RPC: ' + msg)
        return {'robot_state': self.p3d.robot_state,
                'job_state': self.p3d.job_state,
                'job_mode': self.p3d.job_mode
                }        

    # def set_gripper_step(self):  # 10
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_gripper_speed(self):  # 11
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_gripper_min(self):  # 12
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_gripper_press(self):  # 13
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_angular_speed(self):  # 15
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_angular_step(self):  # 16
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_linear_speed(self):  # 17
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def set_lineal_step(self):  # 18
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def endstop(self):  # 20
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    # def move_angular_rel(self):  # 21
    #     msg = 'a('')'
    #     logging.info('RPC: ' + msg)

    def homing(self):  # 22
        msg = 'homing("")'
        logging.debug('RPC in: ' + msg)
        self.p3d.do_inicio('')
        logging.debug('RPC terminada')
        return {'robot_state': self.p3d.robot_state,
                'motors_enabled': self.p3d.motors_enabled,
                'camera_enabled': self.p3d.camera_enabled,
                'coords': self.p3d.coords,
                'mov_mode': self.p3d.mov_mode
                }        

    def move_cartes_rel(self, x, y, z, speed=''):  # 23
        pos = 'r ' + str(x) + ' ' + str(y) + ' ' + str(z)
        if speed != '':
            pos = pos +  ' ' + str(speed)
        msg = 'mcartes("' + pos + '")'
        logging.info('RPC in: ' + msg)
        self.p3d.do_mcartes(pos)
        logging.info('RPC terminada')
        return {'robot_state': self.p3d.robot_state,
                'job_state': self.p3d.job_state,
                'job_mode': self.p3d.job_mode,
                'camera_enabled': self.p3d.camera_enabled,
                'coords': self.p3d.coords,
                'mov_mode': self.p3d.mov_mode
                }        

    def move_cartes_abs(self, x, y, z, speed=''):  # 24
        pos = 'a ' + str(x) + ' ' + str(y) + ' ' + str(z)
        if speed != '':
            pos = pos +  ' ' + str(speed)
        msg = 'mcartes("' + pos + '")'
        logging.info('RPC in: ' + msg)
        self.p3d.do_mcartes(pos)
        logging.info('RPC terminada')
        return {'robot_state': self.p3d.robot_state,
                'job_state': self.p3d.job_state,
                'job_mode': self.p3d.job_mode,
                'camera_enabled': self.p3d.camera_enabled,
                'coords': self.p3d.coords,
                'mov_mode': self.p3d.mov_mode
                }        

    def gripper_move(self):  # 25
        msg = 'mpinza("")'
        logging.info('RPC: ' + msg)

    def gripper_stop(self):  # 26
        msg = 'detener_pinza("")'
        logging.info('RPC: ' + msg)

    def comm_test(self):  # 40
        msg = 'verifica_conexion("")'
        logging.info('RPC in: ' + msg)
        self.p3d.verifica_conexion('')
        logging.info('RPC terminada')
        return {'robot_state': self.p3d.robot_state,
                'camera_enabled': self.p3d.camera_enabled
                }        

    # def sensor_state(self):  # 41
    #     logging.info('RPC: ' + message)

    def connect_camera(self):  # 42
        self.p3d.camara('si')
        msg = 'camara("si")'
        logging.info('RPC: ' + msg)
        return {'robot_state': self.p3d.robot_state,
                'camera_enabled': self.p3d.camera_enabled
                }        

    def disconnect_camera(self):  # 43
        self.p3d.camara('no')
        msg = 'camara("no")'
        logging.info('RPC: ' + msg)
        return {'robot_state': self.p3d.robot_state,
                'camera_enabled': self.p3d.camera_enabled
                }        

    def delay(self):  # 50
        msg = 'a('')'
        logging.info('RPC: ' + msg)

    def mode_manual(self):  # 51
        self.p3d.modo('manual')
        msg = 'modo("manual")'
        logging.info('RPC: ' + msg)
        return {'job_mode': self.p3d.job_mode
                }        

    def mode_auto(self): # 52
        self.p3d.modo('auto')
        msg = 'modo("auto")'
        logging.info('RPC: ' + msg)
        return {'job_mode': self.p3d.job_mode
                }        
  
    def set_time_refresh(self):  # 53
        msg = 'a("")'
        logging.info('RPC: ' + msg)

    def sequence_test(self): 
        self.p3d.do_prueba('')
        msg = 'prueba("")'
        logging.info('RPC: ' + msg)
        return {'coords': self.p3d.coords
                }        

    def on_cooler(self):
        self.p3d.send_now('M106 S127')
        logging.info('RPC: Cooler ON')
        
    def off_cooler(self):
        self.p3d.send_now('M107')
        logging.info('RPC: Cooler OFF')
       
