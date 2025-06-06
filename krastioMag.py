#!/usr/bin/env python
# coding: utf-8
# use pykiba after V3.1  initially aka pykibaNew
#     added timeout before a command sending
#     re.split instead .slplit(',')
#     added '\n' whiele sending 
#     no Walrus operator!
#     Completible with old functions, but renewed 
# V3.1 - added  def install_arduino_commands(self):
#=================================================
#Serves Arduino with krystioMag firmware
#---------------------------------------
#
#hello
#Krastio Magnet
#megaatmega2560
#

from tools import serial_ports_list, print_my_ip, search_by_manufacturer
from pykiba import PykiDev
import jsonpickle
import time


class krastioMag(PykiDev):
    """ Class krastioMag
        Extends PykiDev.
        KrastioMag firmware on the Arduino support 'help' cmd, therefore 
        KrastioMag install all implemented commnads on Arduino in Python.
        Implemented reading of the analog channels trought polynoms.
    """
    def __init__(self, **kargs):
        """ Constructor 
        Parameters
        ----------
            port : device name  e.q. string with /dev/... or comport
            baudrate : int, optional
            The default is 9600. 
            install_cmd: If True install commands from help on Arduino.
            default is False
        Returns
        -------
        None.
        """ 
        super().__init__(**kargs) 
        time.sleep(1)
        self.command("mode 3")
        self.channels_number = len(self.uv())           
        self.poly_dict = {                   #Default polynoms
            "equ" :  [1,0],                  # y = h
            "volts" :  [1.0/1000.0,0]        # y = x/1000
            }
        self.string_rep =  self.string_rep + "\n" + str( self.hello()[0])
        
            
    
    def aread( self, pin = None, calib = None, raw = False):
        """ Reads analog pins, could a calibration polynom be used
        Parameters
        ----------
            pin : 0 to self.channels_number
            calib : "name of a defined polynoms" in self.poly_dict 
            install_cmd: If True install commands from help on Arduino.
            default is False
            raw: Which function to be used ur(raw) or uv
            default is False
        Returns
        -------
        [res] or res = polynom(self.ur() or self.uv)   
        """ 
        if pin != None and pin < self.channels_number:
           if raw:
               tmp_val = self.ur(pin)[1]
           else:
               tmp_val = self.uv(pin)
               
           if calib:
                   tmp_val = self.polynom( tmp_val, calib)
        else:
           if raw:
               tmp_val = [inp[1] for inp in self.ur()]
           else:
               tmp_val = self.uv()
           
           if calib:
               tmp_val = [self.polynom(inp, calib) for inp in tmp_val]
              
        return  tmp_val 


    def polynom(self, arg, name_of_coef):
        """ y = polynom(x)
        Parameters
        ----------
            name_of_coef: key in poly_dict
            arg : ardument x
        Returns
        -------
        res = polynom(x)   
        """ 
        coef = self.poly_dict.get(name_of_coef, None)
        if not coef:
            raise Exception("A polynom not found.")
        
        sum =0
        for tmpi,tmpcc in enumerate(reversed(coef)):
            sum = sum + (pow(arg,tmpi)*tmpcc) 

        return sum
    
    
    def add_polynom(self,  coef, polynom_name):
        """ Adds polynom coef. in self.poly_dict
        Parameters
        ----------
            polynom_name: key in poly_dict
            coef :  [an, ..., a2, a1, a0]  
        Returns
        -------
        Nothing   
        """ 
        self.poly_dict.update({polynom_name : coef})
        
    def polynoms_list(self):  
        """ Prints in a strig self.poly_dict
        Parameters
        ----------
            Nothing
        Returns
        -------
            A string with all poly_dict members   
        """ 
        tmpstr=""
        for key  in self.poly_dict:
            tmpstr+= (f"{key}:{self.poly_dict[key]} , ") 
        return tmpstr
            
    def polynoms_to_file(self, file_name):
        """ Saves self.poly_dict in a file
        Parameters
        ----------
           file_name: the name of the file
        Returns
        -------
            Nothing  
        """ 
        with open(file_name, 'w', newline='') as f:
            print(f"file is opened as {f}") 
            f.write(jsonpickle.encode(self.poly_dict, indent=4 ))
            #f.write("bozakosmata txt")
            f.flush()
        
    def polynoms_from_file(self, file_name):
        """ Read self.poly_dict from a file
        Parameters
        ----------
           file_name: the name of the file
        Returns
        -------
            Nothing  
        """ 
        with open(file_name,'r') as f:   
             string = f.read()     
             self.poly_dict = jsonpickle.decode(string)
     
     
    def defines(self):
        """ Returns self.string_rep
        Parameters
        ----------
           file_name: the name of the file
        Returns
        -------
        """ 
        return self.string_rep
       
    def __repr__(self):
        return self.string_rep
           
    def __str__(self):
        return self.string_rep
        

    def __del__(self):
            self.close()     
            

    
    
   


if __name__ == '__main__':
     serving = False
     serving = True
     #serving = False
     mname = 'Arduino'
     baudrate = 9600
     #
     if not serving:
         lstedPorts = serial_ports_list()
         prt = search_by_manufacturer(lstedPorts ,  mname )
         ard = krastioMag(port = '/dev/ttyACM0', baudrate = baudrate)  # install_cmd = True
         print(ard)
     else:
         import zerorpc
         lstedPorts = serial_ports_list()
         prt = search_by_manufacturer(lstedPorts , mname)
         print(f"Board with a name {mname} connected dev {prt}")
         print("Startin zerorpc server ...")
         print("To IP address")
         print_my_ip()
         print(":4242")  
         s = zerorpc.Server(krastioMag(port =  prt, baudrate = baudrate))
         s.bind("tcp://0.0.0.0:4242")
         s.run()