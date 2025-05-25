# -*- coding: utf-8 -*-
"""
Serves Arduino with krystioMag firmware
---------------------------------------



kamen.p.kamenov@gmail.com
hello
megaatmega2560
Krastio Magnet
"""


#import serial
#import serial.tools.list_ports 
#Terminal on /dev/ttyACM0 | 115200 8-N-1
from pykiba import which_comport_to_use 
from pykiba import Pykiba
import inspect
import jsonpickle
import sys

m_name = 'Arduino (www.arduino.cc)'
hello_str = b'Krastio Magnet\r\n'
s_speed = 115200



class KrystioMagnet():
    
    def __init__(self, speed, mn_name, hello_str = None):
        
        device_port = which_comport_to_use(speed, mn_name, hello_str )
        #device_port = which_comport_to_use(s_speed, m_name)
        
        if device_port:
            self.serial_interface = Pykiba(s_speed, device_port)
            self.serial_interface.command('mode', 2) # the first command always is faulty
            self.serial_interface.command('mode', 2) # led blinks 3 times on connection
            self.channels_number = len(self.uv())
            
        else:
            print("Arduino not found!")
            sys.exit(0)
            
        self.poly_dict = {
                          "equ" :  [1,0],
                          "volts" :  [1,0],
                          "tst_coef" : [3,2,1]}

    def __del__(self):
        self.serial_interface.close()

    def hello(self, *args):
           my_name = inspect.stack()[0][3] #returns name of the function 
           return self.serial_interface.command(my_name, *args) 
                                                
    def mode(self, *args):
           my_name = inspect.stack()[0][3] #returns name of the function 
           return self.serial_interface.command(my_name, *args)
                                                 
    def aur(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)    

    def auv(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)
    
    def ur(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)
                                             
    def uv(self, *args):
       my_name = inspect.stack()[0][3] #returns name of the function 
       return self.serial_interface.command(my_name, *args)

    def calibtoee(self, *args):
       my_name = inspect.stack()[0][3] #returns name of the function 
       return self.serial_interface.command(my_name, *args)

    def calibfromee(self, *args):
       my_name = inspect.stack()[0][3] #returns name of the function 
       return self.serial_interface.command(my_name, *args)

    def setvref(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)
    
    
    def vref(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        
        if(len(args) == 2):
            retval = self.serial_interface.command(my_name, *args)
            
        elif(len(args) == 1):
            for i in range(self.channels_number):
                retval = self.serial_interface.command(my_name, i, args[0])  
                
        else:
               retval = self.serial_interface.command(my_name, *args)    
    
        return  retval 
    
   
    def polynom(self, name_of_coef, arg):
        
        #coef = self.poly_dict[ name_of_coef]
        coef = self.poly_dict.get(name_of_coef, self.poly_dict["equ"])
        sum =0
        for i,c in enumerate(reversed(coef)):
            sum = sum + (pow(arg,i)*c) 
        
        return sum
    
    def add_polynom(self, polynom_name, coef):
        self.poly_dict.update({polynom_name : coef})
        
    def polynoms_list(self):   
        tmpstr=""
        for key  in self.poly_dict:
            tmpstr+= (f'{key}  {self.poly_dict[key]}\n') 
        return tmpstr
            
    def polynoms_to_file(self, file_name):
        # save dictionary to person_data.pkl file
        with open(file_name, 'w', newline='') as f:
            print(f"file is opened as {f}") 
            f.write(jsonpickle.encode(self.poly_dict, indent=4 ))
            #f.write("bozakosmata txt")
            f.flush()
        
    def polynoms_from_file(self, file_name):
        # save dictionary to person_data.pkl file
        with open(file_name,'r') as f:
             
             string = f.read()
             self.poly_dict = jsonpickle.decode(string)

    #def __call__(self, channel, calib = None, raw = False):
    def read(self, channel, calib = None, raw = False):
        
        
        if raw:
            tmp_val = self.ur(channel)[1]

        else:
            tmp_val = self.uv(channel)
            
        if calib:
            tmp_val = self.polynom(calib, tmp_val)
            
            
        return  tmp_val 
            
        
            
            
        


serving = False

if __name__ == '__main__':
    import zerorpc
    
    filename = './polynom.json'
    
    if serving:
        s = zerorpc.Server(KrystioMagnet(s_speed, m_name, hello_str))
        s.bind("tcp://0.0.0.0:4242")
        s.run() 
    
    else:    
        vlt = KrystioMagnet(s_speed, m_name,)
        vlt.polynoms_list()
        
        
        
        #vlt.add_polynom("tst2",[1,2,3])
        #vlt.polynoms_from_file(filename)
        #vlt.polynoms_list()
        #vlt.polynoms_to_file(filename)
        #vlt.add_polynom("tst2",[1,1,1])
        #print(vlt.polynoms_list())
        
        #vlt.set_range(1)
        #print(vlt.set_range())
        #vlt.set_range(2,1)
        #print(vlt.set_range())
        #for i in range(10):
        #    bza1 = vlt(0,calib = "bza",raw = True)
        #    print(f' {vlt(0)} , {bza1} ' )
        #    #print(vlt.ur(0)[1])
        
        #del vlt
    
   
   
    
   

